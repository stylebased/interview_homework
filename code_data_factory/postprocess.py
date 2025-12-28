import json
from pathlib import Path
from typing import Dict, Iterable

from .config import OUTPUT_DIR

SCENE1_RAW = OUTPUT_DIR / "scene1_raw.jsonl"
SCENE2_RAW = OUTPUT_DIR / "scene2_raw.jsonl"
SCENE1_SFT = OUTPUT_DIR / "scene1_sft.jsonl"
SCENE2_SFT = OUTPUT_DIR / "scene2_sft.jsonl"
COMBINED_SFT = OUTPUT_DIR / "combined_sft.jsonl"


def _read_jsonl(path: Path) -> Iterable[Dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def postprocess_scene1():
    records = []
    for r in _read_jsonl(SCENE1_RAW):
        q = r.get("question", "").strip()
        a = r.get("answer", "").strip()
        t = r.get("thinking_trace", "").strip()
        code = r.get("code", "").strip()
        if not q or not a or len(t.split()) < 10:
            continue

        sft = {
            "instruction": q,
            "input": code,
            "output": f"### 思考过程\n{t}\n\n### 回答\n{a}",
            "meta": {
                "file_path": r.get("file_path", ""),
                "class_name": r.get("class_name", ""),
            },
        }
        records.append(sft)

    with SCENE1_SFT.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[Postprocess] Scene1 SFT saved: {SCENE1_SFT} (total {len(records)})")


def postprocess_scene2():
    records = []
    for r in _read_jsonl(SCENE2_RAW):
        inst = r.get("instruction", "").strip()
        t = r.get("thinking_trace", "").strip()
        design = r.get("design_output", {})
        skeleton = r.get("project_skeleton", "")

        if not inst or len(t.split()) < 10 or not design:
            continue

        sft = {
            "instruction": inst,
            "input": f"Project structure:\n{skeleton}",
            "output": (
                "### 架构分析\n"
                f"{t}\n\n"
                "### 设计方案\n"
                f"```json\n{json.dumps(design, ensure_ascii=False, indent=2)}\n```"
            ),
            "meta": {},
        }
        records.append(sft)

    with SCENE2_SFT.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[Postprocess] Scene2 SFT saved: {SCENE2_SFT} (total {len(records)})")


def merge_sft():
    records = list(_read_jsonl(SCENE1_SFT)) + list(_read_jsonl(SCENE2_SFT))
    with COMBINED_SFT.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[Postprocess] Combined SFT saved: {COMBINED_SFT} (total {len(records)})")


def run_all():
    postprocess_scene1()
    postprocess_scene2()
    merge_sft()


if __name__ == "__main__":
    run_all()