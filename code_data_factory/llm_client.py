from typing import List, Dict
import os

from .config import (
    HF_MODEL_NAME,
    MAX_NEW_TOKENS,
    TEMPERATURE,
    DRY_RUN,
)

_hf_model = None
_hf_tokenizer = None




def _get_hf_model():
    global _hf_model, _hf_tokenizer
    if _hf_model is not None:
        return _hf_model, _hf_tokenizer

    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch  # noqa: F401

    print(f"[LLM] Loading HF model: {HF_MODEL_NAME}")
    _hf_tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
    _hf_model = AutoModelForCausalLM.from_pretrained(
        HF_MODEL_NAME,
        torch_dtype="auto",
        device_map="auto",
    )
    return _hf_model, _hf_tokenizer


def chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: int | None = None,
    temperature: float | None = None,
    dry_run: bool | None = None,
) -> str:
    """统一的大模型调用接口，返回纯文本内容。"""
    if dry_run is None:
        dry_run = DRY_RUN
    if max_tokens is None:
        max_tokens = MAX_NEW_TOKENS
    if temperature is None:
        temperature = TEMPERATURE

    if dry_run:
        # 返回一个合法的示例 JSON，方便测试 pipeline
        return """
{
  "samples": [
    {
      "question": "Dummy question?",
      "thinking_trace": "This is a dummy thinking trace for debugging.",
      "answer": "Dummy answer."
    }
  ]
}
"""

    # ---------------- HuggingFace 模式 ----------------
    model, tokenizer = _get_hf_model()

    # 简单把 messages 拼成一个 prompt
    prompt = ""
    for m in messages:
        role = m["role"]
        prefix = "System: " if role == "system" else "User: "
        prompt += prefix + m["content"].strip() + "\n\n"

    import torch

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    pad_id = tokenizer.eos_token_id or tokenizer.pad_token_id or 0

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
            pad_token_id=pad_id,
        )
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    # 只返回新增部分也可以，这里简单处理
    return text