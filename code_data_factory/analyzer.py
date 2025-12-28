import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

from .config import (
    TARGET_REPO_PATH,
    OUTPUT_DIR,
    SUPPORTED_EXTS,
    MAX_CHUNK_CHARS,
)


@dataclass
class CodeChunk:
    file_path: str
    class_name: str
    content_with_lines: str
    language: str = ""
    metadata: Dict = field(default_factory=dict)


def iter_code_files(root: Path) -> Iterable[Path]:
    """遍历代码仓，返回支持的代码文件路径。"""
    for dirpath, dirnames, filenames in os.walk(root):
        # 过滤一些无关目录
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", ".idea", ".vscode", "node_modules", "build", "dist", "target", "__pycache__"}
        ]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTS:
                yield Path(dirpath) / fname


def read_file_with_lines(path: Path) -> str:
    """读取文件内容，并加上行号前缀：'1 | ...'。"""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1", errors="ignore")

    lines = text.splitlines()
    numbered = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered)


def split_into_chunks(numbered_text: str, max_chars: int) -> List[str]:
    """简单按行切块，控制每块长度不超过 max_chars。"""
    if len(numbered_text) <= max_chars:
        return [numbered_text]

    lines = numbered_text.splitlines()
    chunks: List[str] = []
    cur: List[str] = []
    cur_len = 0

    for line in lines:
        l = len(line) + 1
        if cur and cur_len + l > max_chars:
            chunks.append("\n".join(cur))
            cur, cur_len = [], 0
        cur.append(line)
        cur_len += l

    if cur:
        chunks.append("\n".join(cur))
    return chunks


def build_project_tree(root: Path, max_depth: int = 5, max_entries: int = 400) -> str:
    """构建项目目录树的文本表示。"""
    root = root.resolve()
    lines: List[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        depth = len(rel_dir.parts)
        if depth > max_depth:
            continue

        indent = "  " * depth
        if rel_dir == Path("."):
            lines.append(f"{root.name}/")
        else:
            lines.append(f"{indent}{rel_dir.name}/")

        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and d not in {"node_modules", "build", "dist", "target", "__pycache__"}
        ]

        for fname in sorted(filenames):
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTS:
                lines.append(f"{indent}  {fname}")

        if len(lines) > max_entries:
            lines.append("  ... (truncated)")
            break

    return "\n".join(lines)


def extract_manifest_dependencies(root: Path) -> Dict[str, List[str]]:
    """从常见依赖文件(可选)提取依赖信息，方便后续 prompt 使用。"""
    from xml.etree import ElementTree as ET
    deps: Dict[str, List[str]] = {"maven": [], "gradle": [], "npm": [], "pip": []}

    pom = root / "pom.xml"
    if pom.exists():
        try:
            tree = ET.parse(pom)
            for dep in tree.findall(".//dependency"):
                group = dep.findtext("groupId") or ""
                artifact = dep.findtext("artifactId") or ""
                if group and artifact:
                    deps["maven"].append(f"{group}:{artifact}")
        except Exception:
            pass

    gradle = root / "build.gradle"
    if gradle.exists():
        try:
            text = gradle.read_text(encoding="utf-8", errors="ignore")
            import re
            pattern = re.compile(r'(implementation|api|compileOnly|runtimeOnly)\s+["\']([^"\']+)["\']')
            deps["gradle"] = [m.group(2) for m in pattern.finditer(text)]
        except Exception:
            pass

    package_json = root / "package.json"
    if package_json.exists():
        import json as _json
        try:
            data = _json.loads(package_json.read_text(encoding="utf-8"))
            for k, v in data.get("dependencies", {}).items():
                deps["npm"].append(f"{k}@{v}")
            for k, v in data.get("devDependencies", {}).items():
                deps["npm"].append(f"{k}@{v}")
        except Exception:
            pass

    req = root / "requirements.txt"
    if req.exists():
        try:
            lines = req.read_text(encoding="utf-8", errors="ignore").splitlines()
            deps["pip"] = [
                line.strip() for line in lines
                if line.strip() and not line.strip().startswith("#")
            ]
        except Exception:
            pass

    return deps


def run_analysis():
    """总入口：扫描代码仓，生成 skeleton + chunks。"""
    root = TARGET_REPO_PATH
    if not root.exists():
        raise FileNotFoundError(f"TARGET_REPO_PATH 不存在: {root}")

    print(f"[Analyzer] Scanning repo: {root}")

    # 1. 目录树
    tree_text = build_project_tree(root)
    (OUTPUT_DIR / "project_skeleton.txt").write_text(tree_text, encoding="utf-8")
    print(f"[Analyzer] Project tree saved to: {OUTPUT_DIR / 'project_skeleton.txt'}")

    # 2. 依赖信息
    deps = extract_manifest_dependencies(root)

    # 3. 代码分块
    chunks: List[Dict] = []
    for path in iter_code_files(root):
        numbered = read_file_with_lines(path)
        for chunk_text in split_into_chunks(numbered, MAX_CHUNK_CHARS):
            chunks.append(
                CodeChunk(
                    file_path=str(path),
                    class_name=path.stem,
                    content_with_lines=chunk_text,
                    language=path.suffix.lstrip("."),
                    metadata={"deps": deps},
                ).__dict__
            )

    chunks_path = OUTPUT_DIR / "chunks.json"
    chunks_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Analyzer] Code chunks saved to: {chunks_path} (total {len(chunks)} items)")

    # 4. skeleton.json
    skeleton_json = {
        "root": str(root),
        "paths": sorted(
            {str(p.relative_to(root)) for p in iter_code_files(root)}
        ),
        "dependencies": deps,
    }
    (OUTPUT_DIR / "project_skeleton.json").write_text(
        json.dumps(skeleton_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[Analyzer] Path list saved to: {OUTPUT_DIR / 'project_skeleton.json'}")


if __name__ == "__main__":
    run_analysis()