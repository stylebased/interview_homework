
"""
Scene 2: Generate system / architectural design proposals based on a project structure.
"""

from __future__ import annotations

import argparse
import json
import random
from typing import Dict, List, Optional

from .config_clean import OUTPUT_DIR
from .llm_client_clean import chat_completion


SKELETON_JSON_PATH = OUTPUT_DIR / "project_skeleton.json"
SCENE2_RAW_PATH = OUTPUT_DIR / "scene2_raw.jsonl"


def load_project_skeleton() -> List[str]:
    if not SKELETON_JSON_PATH.exists():
        raise FileNotFoundError(f"Project skeleton not found: {SKELETON_JSON_PATH}")
    with SKELETON_JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list in {SKELETON_JSON_PATH}, got {type(data)}")
    return data


def build_messages_for_design(
    project_files: List[str],
    sample_files: List[str],
    design_count: int,
) -> List[Dict[str, str]]:
    """Build prompt messages for Scene 2 system design generation."""

    system = (
        "You are a senior software architect. "
        "You design new features that fit into an existing codebase. "
        "You must provide clear reasoning and final design specifications. "
        "Respond in strict JSON only."
    )

    project_overview = "\n".join(f"- {p}" for p in project_files)
    samples_overview = "\n".join(f"- {p}" for p in sample_files)

    user = f"""
Existing project structure (partial):

{project_overview}

Representative files (subset):

{samples_overview}

Task:
1. Propose {design_count} realistic new features or enhancements that could be added
to this project. They should be consistent with the existing structure and naming.
2. For each feature, provide a detailed thinking_trace explaining:
- why this feature makes sense,
- how it fits into the architecture,
- what modules or layers it touches,
- what trade-offs you considered.
3. Then write a design_spec describing the final design in a concise, implementable way.

Output STRICTLY as JSON (no comments, no extra text):

{{
"plans": [
{{
  "feature_title": "string",
  "thinking_trace": "string, multi-step reasoning",
  "design_spec": "string, final proposed design"
}}
]
}}
"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t.lstrip("json").lstrip()
    return t


def parse_scene2_response(raw: str) -> List[Dict[str, str]]:
    """Parse LLM JSON response into a list of plans."""
    raw = _strip_code_fence(raw)

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

        if isinstance(obj, dict) and "plans" in obj:
            plans = obj["plans"]
        elif isinstance(obj, list):
            plans = obj
        else:
            continue

        if not isinstance(plans, list):
            continue

        cleaned: List[Dict[str, str]] = []
        for p in plans:
            if not isinstance(p, dict):
                continue
            title = (p.get("feature_title") or "").strip()
            trace = (p.get("thinking_trace") or "").strip()
            spec = (p.get("design_spec") or "").strip()
            if not title or not spec or len(trace.split()) < 5:
                continue
            cleaned.append(
                {
                    "feature_title": title,
                    "thinking_trace": trace,
                    "design_spec": spec,
                }
            )
        return cleaned

    return []


def generate_scene2(
    count: int = 5,
    sample_file_count: int = 20,
    dry_run: Optional[bool] = None,
) -> int:
    """Generate Scene-2 design data."""
    files = load_project_skeleton()
    if not files:
        print("[Scene2] No project files found in project_skeleton.json")
        return 0

    SCENE2_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    with SCENE2_RAW_PATH.open("w", encoding="utf-8") as f_out:
        for i in range(count):
            print(f"[Scene2] Generating design batch {i + 1}/{count}")

            sample_files = random.sample(files, min(sample_file_count, len(files)))
            messages = build_messages_for_design(files, sample_files, design_count=1)

            try:
                resp_text = chat_completion(messages, dry_run=dry_run, scene="scene2")
            except Exception as e:
                print(f"[Scene2] ERROR calling LLM: {e}")
                continue

            plans = parse_scene2_response(resp_text)
            if not plans:
                print("[Scene2] WARNING: Could not parse response")
                continue

            for plan in plans:
                record = {
                    "project_files": files,
                    "sample_files": sample_files,
                    "feature_title": plan["feature_title"],
                    "thinking_trace": plan["thinking_trace"],
                    "design_spec": plan["design_spec"],
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total += 1

    print(f"[Scene2] Done. Total plans: {total}. Saved to: {SCENE2_RAW_PATH}")
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scene 2: generate system design data from project skeleton."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="How many design batches to generate.",
    )
    parser.add_argument(
        "--sample-file-count",
        type=int,
        default=20,
        help="How many project files to include in each prompt as context.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use dry-run mode (if supported by llm_client).",
    )

    args = parser.parse_args()
    generate_scene2(
        count=args.count,
        sample_file_count=args.sample_file_count,
        dry_run=args.dry_run,
    )
