import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


@st.cache_resource
def load_heavy_model():
    """
    Load the 7B creative model once and cache it.
    """
    model_name = "Qwen/Qwen2.5-7B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return tokenizer, model


def generate_with_heavy_model(prompt: str, max_new_tokens: int = 300) -> str:
    tokenizer, model = load_heavy_model()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result
