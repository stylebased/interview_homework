# interview_homework
Codebase Data Factory

A framework for automatically generating high-quality training datasets from real software projects — including:

Code Understanding (Q&A)

System Design / Architecture Reasoning

The pipeline:

Analyzes an existing codebase

Extracts structure and code snippets

Prompts an LLM to generate realistic tasks

Outputs structured datasets suitable for SFT (Supervised Fine-Tuning)

✨ Features

✔ Analyze any local or open-source repository

✔ Two realistic scenarios

Scene-1: Code Q&A (understanding + reasoning)

Scene-2: System design + architecture planning

✔ JSONL datasets for training

✔ DRY-RUN testing mode (no LLM required)

✔ Modular and extendable

📂 Project Structure
code_data_factory/
 ├── analyzer.py          # Analyze repository, extract structure + code chunks
 ├── scene1_pipeline.py   # Generate Code Q&A dataset
 ├── scene2_pipeline.py   # Generate System Design dataset
 ├── postprocess.py       # Clean + merge into final SFT dataset
 ├── llm_client.py        # Wrapper for local / HF / OpenAI models
 ├── config.py            # Configuration settings
 └── cli.py               # Command-line interface


Generated data appears under:

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


Create a virtual environment:

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

🎯 Select a Target Codebase

Clone any project you want to analyze, for example:

git clone https://github.com/halo-dev/halo.git halo-main


Set environment variable:

export TARGET_REPO_PATH=/path/to/halo-main


Windows PowerShell:

setx TARGET_REPO_PATH "C:\path\to\halo-main"

🧪 DRY-RUN Mode (Recommended First)

Run everything without calling an actual LLM:

export DRY_RUN=1


This tests pipeline logic safely.

🚀 Usage
1️⃣ Analyze repository
python main.py analyze

2️⃣ Generate Scene-1 (Code Q&A)
python main.py scene1 --limit 20 --qa-count 3 --dry-run

3️⃣ Generate Scene-2 (System Design)
python main.py scene2 --count 5 --dry-run

4️⃣ Post-process and merge datasets
python main.py postprocess

🤖 Using a Real LLM (Optional)
Option A — HuggingFace Local Model
export DRY_RUN=0
export HF_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"

Option B — OpenAI-Compatible API
export DRY_RUN=0
export USE_OPENAI=1
export OPENAI_API_KEY=YOUR_KEY

📌 Output Overview
File	Description
project_skeleton.*	Compressed view of project structure
chunks.json	Extracted code segments
scene1_raw.jsonl	Raw Q&A responses
scene1_sft.jsonl	Cleaned dataset for Scene-1
scene2_raw.jsonl	Raw architecture designs
scene2_sft.jsonl	Cleaned dataset for Scene-2
combined_sft.jsonl	Final merged dataset
✅ Why This Project Matters

This pipeline demonstrates:

automated dataset creation

support for multiple training tasks

realistic development scenarios

structured, reusable design

explainable outputs (thinking traces included)

ability to run without a model first (dry-run)

⚠️ Notes

Large repositories may take time to process

Avoid scanning folders like:

node_modules
build
dist
.git


Always test using DRY_RUN first
