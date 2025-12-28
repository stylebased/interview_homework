# interview_homework
Codebase Data Factory

A framework for automatically generating high-quality training datasets from real software projects — including
code understanding (Q&A) and system design (architecture reasoning).

This repository builds a pipeline that:

Analyzes an existing codebase

Extracts structure and code snippets

Prompts an LLM to generate realistic tasks

Produces structured training datasets suitable for SFT (Supervised Fine-Tuning)

✨ Features

✔ Automatically analyze any local or open-source repository
✔ Generate two training scenarios:

1️⃣ Scene-1: Code Q&A (understanding, reasoning, business context)
2️⃣ Scene-2: System design (architecture planning, explanation, trace)

✔ Structured JSONL dataset outputs
✔ DRY-RUN mode (no LLM required for testing)
✔ Extensible and modular framework

📂 Project Structure
code_data_factory/
 ├── analyzer.py          # Analyze repository, build skeleton, extract chunks
 ├── scene1_pipeline.py   # Generate Code Q&A dataset
 ├── scene2_pipeline.py   # Generate System Design dataset
 ├── postprocess.py       # Clean and merge data into final SFT format
 ├── llm_client.py        # Wrapper for local/HF/OpenAI models
 ├── config.py            # Global configuration
 └── cli.py               # Command line entrypoint


Generated data is stored under:

data/
 ├── project_skeleton.txt
 ├── project_skeleton.json
 ├── chunks.json
 ├── scene1_raw.jsonl
 ├── scene1_sft.jsonl
 ├── scene2_raw.jsonl
 ├── scene2_sft.jsonl
 └── combined_sft.jsonl

🛠 Installation

Clone the repository:

git clone YOUR_REPO_URL
cd codebase-data-factory


Create virtual environment:

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

🎯 Select a Target Codebase

Clone any public project (or your own project):

Example:

git clone https://github.com/halo-dev/halo.git halo-main


Set environment variable:

export TARGET_REPO_PATH=/path/to/halo-main


Windows PowerShell:

setx TARGET_REPO_PATH "C:\path\to\halo-main"

🧪 DRY-RUN Mode (recommended first)

Run the full pipeline without calling any real LLM:

export DRY_RUN=1


This allows you to test pipeline logic safely.

🚀 Usage
Step 1 — Analyze repository
python main.py analyze

Step 2 — Generate Scene-1 (Code Q&A)
python main.py scene1 --limit 20 --qa-count 3 --dry-run

Step 3 — Generate Scene-2 (System Design)
python main.py scene2 --count 5 --dry-run

Step 4 — Post-process and merge datasets
python main.py postprocess

🤖 Using a real LLM (optional)
Option A — HuggingFace local model

In environment:

export DRY_RUN=0
export HF_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"

Option B — OpenAI-compatible API
export DRY_RUN=0
export USE_OPENAI=1
export OPENAI_API_KEY=YOUR_KEY

📌 Output Overview

This project automatically produces:

File	Description
project_skeleton.*	Compact representation of project structure
chunks.json	Extracted code segments
scene1_raw.jsonl	Raw Q&A generation
scene1_sft.jsonl	Cleaned SFT dataset (Scene-1)
scene2_raw.jsonl	Raw design outputs
scene2_sft.jsonl	Cleaned SFT dataset (Scene-2)
combined_sft.jsonl	Final merged dataset
✅ Assignment Alignment

This project satisfies:

✔ Two real scenarios (Q&A + architecture design)
✔ Automated training-data pipeline
✔ Reusable, extensible design
✔ Works on open-source or private repositories
✔ Produces reasoning + explanation traces
✔ Includes dry-run validation capability

👀 Notes

Large repositories may take longer to scan

Avoid scanning folders like node_modules, build, .git

Always test with DRY_RUN first
