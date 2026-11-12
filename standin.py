import asyncio
import random
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="The Relay Stand-in Model")

class Request(BaseModel):
    prompt: str
    simulated_load: int = 1
    fail_probability: float = 0.03
    base_latency_ms: int = 700
    token_limit: int = 8000

@app.post("/generate")
async def generate(req: Request):
    if req.token_limit <= 0:
        raise HTTPException(status_code=429, detail="Simulated daily token budget exhausted")
    load_delay = max(0, req.simulated_load - 1) * 120
    delay = req.base_latency_ms + load_delay + random.randint(0, 350)
    await asyncio.sleep(delay / 1000)
    if random.random() < req.fail_probability:
        raise HTTPException(status_code=503, detail="Simulated upstream failure")
    text = "Stand-in response: " + req.prompt[:240]
    return {"text": text, "latency_ms": delay, "tokens_in": len(req.prompt.split()),
            "tokens_out": len(text.split()), "source": "stand-in"}

@app.get("/health")
def health():
    return {"status": "ok"}
