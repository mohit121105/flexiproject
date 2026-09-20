"""
app/llm_fallback.py
Groq Fallback Integration

Provides automatic fallback to Groq (openai/gpt-oss-120b or qwen/qwen3.8-27b)
whenever Gemini API encounters rate limits, quota issues, or downtime.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_BACKUP_MODEL = "qwen/qwen3.8-27b"


def call_groq_chat(
    prompt: str,
    system_prompt: str = None,
    temperature: float = 0.5,
    max_tokens: int = 1500,
    json_mode: bool = False,
) -> str:
    """
    Execute a chat completion on Groq as a fallback LLM.
    
    Args:
        prompt: User message / task description
        system_prompt: Optional system instruction
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        json_mode: Whether to instruct JSON formatting
        
    Returns:
        Generated text string from Groq
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Try primary model, fallback to backup model if needed
    for model_name in [GROQ_MODEL, GROQ_BACKUP_MODEL]:
        try:
            kwargs = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if content:
                print(f"[GROQ FALLBACK] Successfully served response via {model_name}")
                return content.strip()
        except Exception as e:
            print(f"[GROQ FALLBACK] Model {model_name} failed: {e}. Trying next...")

    raise RuntimeError("All Groq models failed to generate response.")
