import time
from groq import Groq

class GroqModel:
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key, timeout=45.0, max_retries=0)
        self.model = model

    def complete(self, messages: list[dict], max_tokens: int = 700) -> dict:
        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=max_tokens,
            stream=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        usage = getattr(response, "usage", None)
        return {
            "text": response.choices[0].message.content or "",
            "tokens_in": getattr(usage, "prompt_tokens", None),
            "tokens_out": getattr(usage, "completion_tokens", None),
            "elapsed_ms": elapsed_ms,
            "model": self.model,
        }
