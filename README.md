# Codebase Data Factory

An automated pipeline to generate high-quality SFT training datasets from local code repositories.  
This system focuses on two core scenarios:

1. **Business Logic Q&A Generation (Scene-1)**  
2. **Architectural Design Proposal Generation (Scene-2)**

Both scenarios include **explicit reasoning traces** (“Thinking Trace”) to help fine-tune large language models for project-specific understanding.


## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

*   **[Design Document](docs/design_doc.md)**: System architecture, dataset schema, and generation strategies.
*   **[Configuration Guide](docs/configuration.md)**: Detailed explanation of environment variables and settings.

## ✨ Key Features

### 1. Scene-1: Business Logic Q&A

- Extracts business logic and developer behavior from code chunks.
- Generates realistic question–reasoning–answer triplets.
- Emphasizes clear explanation of *why* the code behaves a certain way.
- Helps models learn how to reason step-by-step about code.

**Typical outputs:**

| Field | Description |
|-------|-------------|
| question | Developer-level or business-level query about code |
| thinking_trace | Step-by-step reasoning process used by model |
| answer | Concise and accurate explanation |

---

### 2. Scene-2: Architectural Design Proposal

- Uses project structure and representative snippets to generate design proposals.
- Simulates new realistic feature requirements based on existing patterns.
- Produces structured outputs covering:
  - API changes
  - Domain model updates
  - Data storage considerations
  - Workflow and orchestration
- Includes reasoning traces explaining architectural decisions.

---

## 🛠 Usage

### Prerequisites

- Python 3.9+

---

## 📦 Requirements

```bash
# Clone the repository
git clone https://github.com/your-username/local-repo-trainer.git
cd local-repo-trainer
```

This project uses Python 3.9+.

Install dependencies using:
```bash
pip install -r requirements.txt
```
### Running the Generator
## Scenario 1 — Business Q&A Generation
```bash
# Dry-run (simulation, no API calls)
python3 main.py scene1 --limit 5 --dry-run
# Actual generation
python3 main.py scene1 --limit 100 --qa-count 3
```

## Scenario 2 — Architectural Design Generation
```bash
# Dry-run
python3 main.py scene2 --count 2 --dry-run

# Actual generation
python3 main.py scene2 --count 50
```
## 📁 Output Directory
Generated files are saved under:
```bash
data/
├── scene1_raw.jsonl          # Raw Scene-1 outputs
├── scene1_sft.jsonl          # Cleaned Scene-1 dataset
├── scene2_raw.jsonl          # Raw Scene-2 outputs
├── scene2_sft.jsonl          # Cleaned Scene-2 dataset
├── combined_sft.jsonl        # Merged dataset for fine-tuning
├── project_skeleton.txt
├── project_skeleton.json
└── chunks.json
```
The final training dataset combined_sft.jsonl contains both Scene-1 and Scene-2 samples.

## 📦 Example Output

Generated dataset samples include:

-- Business questions about real code behavior

-- Reasoning traces showing how answers were derived

-- Structured architectural design proposals with context

## ⚠️ Notes & Tips

-- Use dry-run mode first to validate the pipeline without cost.

-- Choose reasonable chunk limits for large repositories.










These samples can be used directly for supervised fine-tuning of LLMs.
