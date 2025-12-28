from pathlib import Path
import os

# 目标代码仓路径：你可以改默认值，或用环境变量覆盖
TARGET_REPO_PATH = Path(
    os.getenv("TARGET_REPO_PATH", "../halo-main")  # TODO: 改成你自己的代码仓路径
).resolve()

# 输出目录
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./data")).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 支持的代码后缀
SUPPORTED_EXTS = {
    ".py", ".js", ".ts", ".java", ".kt",
    ".go", ".cpp", ".c", ".cs", ".rs",
    ".swift", ".php", ".rb", ".h",
}

# 代码分块最大长度（字符数）
MAX_CHUNK_CHARS = int(os.getenv("MAX_CHUNK_CHARS", "4000"))

# 模型配置（HuggingFace）
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "768"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.35"))

# 是否干跑（不真的调用模型，返回假数据）——默认先开着，确认流程没问题
DRY_RUN = os.getenv("DRY_RUN", "1") == "1"