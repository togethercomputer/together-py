import asyncio
import os
import time
from typing import List, Any
from together import AsyncTogether

# --- CONFIGURATION ---
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo" # Together's flagship high-speed model
MAX_CONCURRENCY = 50  # The "sweet spot" for high-tier accounts
RETRIES = 3

class TogetherBatchEngine:
    def __init__(self, api_key: str, concurrency: int = 20):
        self.client = AsyncTogether(api_key=api_key)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def process_single_prompt(self, prompt: str, index: int):
        """Worker that handles one request with a safety lock (semaphore)"""
        async with self.semaphore:
            for attempt in range(RETRIES):
                try:
                    # v2.0 SDK Syntax
                    response = await self.client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=512,
                        temperature=0.7
                    )
                    return {"index": index, "result": response.choices[0].message.content, "status": "success"}
                except Exception as e:
                    if attempt == RETRIES - 1:
                        return {"index": index, "error": str(e), "status": "failed"}
                    # Exponential Backoff
                    await asyncio.sleep(2 ** attempt)

    async def run_batch(self, prompts: List[str]):
        """Orchestrator that fires off thousands of tasks"""
        start_time = time.perf_counter()
        
        # Create all tasks immediately
        tasks = [self.process_single_prompt(p, i) for i, p in enumerate(prompts)]
        
        # Gather with progress tracking (optional: use tqdm here)
        results = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_time
        print(f"--- BATCH COMPLETE ---")
        print(f"Processed {len(prompts)} prompts in {total_time:.2f} seconds")
        print(f"Throughput: {len(prompts)/total_time:.2f} requests/sec")
        return results

# --- EXECUTION ---
async def main():
    # 100 sample prompts (Scale this to 10,000 if you want)
    test_prompts = [f"Explain the physics of a black hole, part {i}" for i in range(100)]
    
    engine = TogetherBatchEngine(api_key=TOGETHER_API_KEY, concurrency=MAX_CONCURRENCY)
    final_results = await engine.run_batch(test_prompts)
    
    # Save or inspect results
    # print(final_results[0]['result'])

if __name__ == "__main__":
    asyncio.run(main())
