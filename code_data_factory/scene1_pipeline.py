
# -*- coding: utf-8 -*-
"""
场景 1：基于代码片段生成“代码 / 业务”问答对。
（已将注释与说明改为中文）
"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

# 结果输出目录
from .config import OUTPUT_DIR

# LLM 客户端
from .llm_client import chat_completion

# ---------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------

CHUNKS_PATH = OUTPUT_DIR / "chunks.json"
SCENE1_RAW_PATH = OUTPUT_DIR / "scene1_raw.jsonl"


def load_chunks(limit: Optional[int] = None) -> List[Dict]:
    """
    从 chunks.json 中加载代码片段。
    """
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"未找到: {CHUNKS_PATH}")
    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    if limit is not None:
        chunks = chunks[:limit]
    return chunks


def build_messages_for_chunk(chunk: Dict, qa_count: int):
    """构建 LLM 输入消息"""
    system = (
        "You are a senior software engineer. "
        "You MUST answer in strict JSON."
    )

    user = f"""
代码（带行号）：

{chunk.get("content_with_lines","")}

任务：生成 {qa_count} 个问题 + 推理 + 答案（严格 JSON）
"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _strip_code_fence(text: str) -> str:
    """去除 ```json 包裹"""
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t.lstrip("json").lstrip()
    return t


def parse_llm_response(raw: str):
    """解析 LLM JSON 输出"""
    raw = _strip_code_fence(raw)
    try:
        obj = json.loads(raw)
    except Exception:
        return []
    return obj.get("samples", [])


def generate_scene1(limit: int = 50, qa_count: int = 3, dry_run=None) -> int:
    """主流程"""
    chunks = load_chunks(limit=limit)
    SCENE1_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    with SCENE1_RAW_PATH.open("w", encoding="utf-8") as f_out:
        for chunk in chunks:
            messages = build_messages_for_chunk(chunk, qa_count)
            resp = chat_completion(messages, dry_run=dry_run)
            samples = parse_llm_response(resp)
            for s in samples:
                f_out.write(json.dumps(s, ensure_ascii=False) + "\n")
                total += 1
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--qa-count", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    generate_scene1(args.limit, args.qa_count, args.dry_run)

