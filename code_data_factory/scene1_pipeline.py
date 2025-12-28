
"""
场景 1：从代码片段生成 “代码 / 业务” 问答对。

流程：

从 data/chunks.json（由 analyzer 生成）读取代码片段。

对于每个代码片段，让 LLM：

生成真实、贴近实际的问题

产出 thinking_trace（逐步推理过程）

给出最终答案

将所有结果保存到 data/scene1_raw.jsonl。

真正符合 SFT 格式的整理工作，会在后续由 postprocess.py 来完成。
"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

from .config import OUTPUT_DIR
from .llm_client import chat_completion


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

CHUNKS_PATH = OUTPUT_DIR / "chunks.json"
SCENE1_RAW_PATH = OUTPUT_DIR / "scene1_raw.jsonl"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_chunks(limit: Optional[int] = None) -> List[Dict]:
    """
    Load code chunks from chunks.json.

    Each chunk is expected to look like:
    {
      "file_path": "...",
      "class_name": "...",
      "content_with_lines": "...",
      ...
    }
    """
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Chunk file not found: {CHUNKS_PATH}")

    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list):
        raise ValueError(f"Expected a list in {CHUNKS_PATH}, got {type(chunks)}")

    if limit is not None:
        chunks = chunks[:limit]

    return chunks


def build_messages_for_chunk(chunk: Dict, qa_count: int) -> List[Dict[str, str]]:
    """
    Build the chat-style messages for one code chunk.
    The model is asked to return STRICT JSON.
    """
    file_path = chunk.get("file_path", "")
    class_name = chunk.get("class_name", "")
    code = chunk.get("content_with_lines", "")

    system = (
        "You are a senior software engineer. "
        "You read code and generate developer-style questions, step-by-step reasoning, "
        "and clear answers. You MUST respond in strict JSON only."
    )

    user = f"""
            File path: {file_path}
            Class / module: {class_name}

            Code (with line numbers):

            ```text
            {code}
            ```

            Task:

            Propose {qa_count} realistic questions a developer or product owner might ask
            about this code (behavior, intent, edge cases, business logic, etc.).

            For each question, write a detailed thinking_trace that explains, step by step,
            how you reason about the code to reach an answer.

            Then give a concise final answer.

            Output STRICTLY as JSON (no comments, no extra text):

            {{
              "samples": [
                {{
                  "question": "string",
                  "thinking_trace": "string, multi-step reasoning",
                  "answer": "string, concise answer"
                }}
              ]
            }}
            """

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _strip_code_fence(text: str) -> str:
    """Remove ```json code fences if present."""
    t = text.strip()
    if t.startswith("```"):
        # remove surrounding backticks
        t = t.strip("`")
        # drop optional language tag like "json"
        t = t.lstrip("json").lstrip()
    return t


def parse_llm_response(raw: str) -> List[Dict[str, str]]:
    """
    Parse the LLM response into a list of dicts:
    [{question, thinking_trace, answer}, ...]
    """
    raw = _strip_code_fence(raw)

    # Try full JSON first, then substring between the first { and last }
    candidates = [raw]
    if "{" in raw and "}" in raw:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < end:
            candidates.append(raw[start : end + 1])

    for c in candidates:
        try:
            obj = json.loads(c)
        except json.JSONDecodeError:
            continue

        # Expected: {"samples": [...]} or directly a list
        if isinstance(obj, dict) and "samples" in obj:
            samples = obj["samples"]
        elif isinstance(obj, list):
            samples = obj
        else:
            continue

        if not isinstance(samples, list):
            continue

        cleaned: List[Dict[str, str]] = []
        for s in samples:
            if not isinstance(s, dict):
                continue
            q = (s.get("question") or "").strip()
            trace = (s.get("thinking_trace") or "").strip()
            ans = (s.get("answer") or "").strip()
            # Filter out empty / trivial entries
            if not q or not ans or len(trace.split()) < 5:
                continue
            cleaned.append(
                {
                    "question": q,
                    "thinking_trace": trace,
                    "answer": ans,
                }
            )
        return cleaned

    # Parsing failed
    return []


# ---------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------

def generate_scene1(
    limit: int = 50,
    qa_count: int = 3,
    dry_run: Optional[bool] = None,
) -> int:
    """
    Main function to generate Scene-1 data.

    Args:
        limit: Max number of chunks to load from chunks.json.
        qa_count: Number of Q&A pairs to ask for each chunk.
        dry_run: If True, llm_client may use dummy data instead of real LLM calls.
                 If None, uses llm_client's default behavior.

    Returns:
        Total number of Q&A samples written.
    """
    chunks = load_chunks(limit=limit)
    SCENE1_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    total = 0

    with SCENE1_RAW_PATH.open("w", encoding="utf-8") as f_out:
        for idx, chunk in enumerate(chunks, start=1):
            file_path = chunk.get("file_path", "")
            print(f"[Scene1] Processing chunk {idx}/{len(chunks)}: {file_path}")

            messages = build_messages_for_chunk(chunk, qa_count=qa_count)

            try:
                resp_text = chat_completion(messages, dry_run=dry_run)
            except Exception as e:
                print(f"[Scene1] ERROR calling LLM for {file_path}: {e}")
                continue

            samples = parse_llm_response(resp_text)
            if not samples:
                print(f"[Scene1] WARNING: Could not parse response for {file_path}")
                continue

            for s in samples:
                record = {
                    "file_path": file_path,
                    "class_name": chunk.get("class_name", ""),
                    "code": chunk.get("content_with_lines", ""),
                    "question": s["question"],
                    "thinking_trace": s["thinking_trace"],
                    "answer": s["answer"],
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total += 1

    print(f"[Scene1] Done. Total samples: {total}. Saved to: {SCENE1_RAW_PATH}")
    return total


# ---------------------------------------------------------------------
# CLI wrapper
# ---------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scene 1: generate code/business Q&A data from code chunks."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of chunks to process from chunks.json",
    )
    parser.add_argument(
        "--qa-count",
        type=int,
        default=3,
        help="Number of Q&A pairs to request per chunk",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use dry-run mode (if supported by llm_client).",
    )

    args = parser.parse_args()
    generate_scene1(limit=args.limit, qa_count=args.qa_count, dry_run=args.dry_run)


