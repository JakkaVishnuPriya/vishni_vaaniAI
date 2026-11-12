"""Basic async load generator for the stand-in service. Save raw run logs separately."""
import argparse, asyncio, csv, time, uuid
import httpx

async def one(client, url, scenario, prompt, sem, writer, lock):
    async with sem:
        start = time.time()
        status, first_token_ms, total_ms = "error", "", ""
        try:
            response = await client.post(url, json={"prompt": prompt, "simulated_load": 1})
            total_ms = (time.time() - start) * 1000
            status = "ok" if response.status_code == 200 else "error"
        except Exception:
            total_ms = (time.time() - start) * 1000
        row = [str(uuid.uuid4()), scenario, "stand-in", start, first_token_ms, total_ms,
               status, 0, len(prompt.split()), "", "hierarchical"]
        async with lock:
            writer.writerow(row)

async def main(args):
    fields = ["request_id","scenario","source","start_time","first_token_ms","total_ms",
              "status","retries","tokens_in","tokens_out","retrieval_setting"]
    lock = asyncio.Lock()
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(fields)
        sem = asyncio.Semaphore(args.concurrency)
        async with httpx.AsyncClient(timeout=60) as client:
            await asyncio.gather(*[
                one(client, args.url, args.scenario, f"test request {i}", sem, writer, lock)
                for i in range(args.requests)
            ])

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8001/generate")
    p.add_argument("--requests", type=int, default=30)
    p.add_argument("--concurrency", type=int, default=5)
    p.add_argument("--scenario", default="steady")
    p.add_argument("--output", default="results/standin_run.csv")
    asyncio.run(main(p.parse_args()))
