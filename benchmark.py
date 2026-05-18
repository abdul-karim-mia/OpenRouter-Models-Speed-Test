import os
import json
import time
import sys
import argparse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description="OpenRouter LLM Speed Benchmark")
group = parser.add_mutually_exclusive_group()
group.add_argument("--resume", action="store_true", help="Continue from last completed model (default)")
group.add_argument("--restart", action="store_true", help="Delete results.json and start from scratch")
args = parser.parse_args()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
PROMPT = "What is the capital of India? Please answer in one sentence."
RESULTS_FILE = "results.json"
RATE_LIMIT_WAIT = 12  # seconds to wait on 429
REQUEST_TIMEOUT = 60  # seconds before giving up on a hung model

if not API_KEY:
    print("❌ Error: OPENROUTER_API_KEY environment variable not set")
    print("Set it with: $env:OPENROUTER_API_KEY = 'your-key-here'")
    sys.exit(1)

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=REQUEST_TIMEOUT)

with open("models.json") as f:
    models = json.load(f)

# Load existing results so we can resume
if args.restart and os.path.exists(RESULTS_FILE):
    os.remove(RESULTS_FILE)
    print("🗑  Deleted results.json — starting fresh.")

try:
    with open(RESULTS_FILE) as f:
        results = json.load(f)
    done_ids = {r["id"] for r in results}
    print(f"Resuming — {len(done_ids)} models already done, {len(models) - len(done_ids)} remaining.")
except FileNotFoundError:
    results = []
    done_ids = set()
    print(f"Starting fresh — {len(models)} models to benchmark.")


def benchmark_model(model_id, label):
    print(f"\n→ {label} ({model_id})")
    try:
        start = time.perf_counter()
        token_count = 0
        first_token_time = None

        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": PROMPT}],
            stream=True,
        )

        for chunk in response:
            if not first_token_time:
                first_token_time = time.perf_counter() - start
            if chunk.choices[0].delta.content:
                token_count += 1

        total_time = time.perf_counter() - start
        tps = token_count / total_time if total_time > 0 else 0
        response_text = response.choices[0].message.content if hasattr(response, "choices") else ""

        result = {
            "id": model_id,
            "label": label,
            "status": "ok",
            "total_time_s": round(total_time, 3),
            "tokens": token_count,
            "tokens_per_second": round(tps, 2),
            "ttft_s": round(first_token_time, 3) if first_token_time else None,
            "response_preview": response_text[:100] if response_text else "",
        }
        print(f"   ✓ {token_count} tokens in {total_time:.2f}s ({tps:.2f} t/s)")
        return result

    except Exception as e:
        error_msg = str(e)
        print(f"   ✗ Error: {error_msg[:60]}...")
        return {
            "id": model_id,
            "label": label,
            "status": "error",
            "error": error_msg,
            "total_time_s": None,
            "tokens": 0,
            "tokens_per_second": 0,
            "ttft_s": None,
        }


# Main benchmark loop
for model in models:
    if model["id"] in done_ids:
        print(f"⊘ {model['label']} ({model['id']}) — already done")
        continue

    result = benchmark_model(model["id"], model["label"])
    results.append(result)

    # Save after each model
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Rate limiting
    if result["status"] == "ok":
        print(f"   (waiting {RATE_LIMIT_WAIT}s before next...)")
        time.sleep(RATE_LIMIT_WAIT)

# Final summary
print("\n" + "=" * 60)
print("BENCHMARK COMPLETE")
print("=" * 60)
ok_count = sum(1 for r in results if r["status"] == "ok")
error_count = sum(1 for r in results if r["status"] == "error")
print(f"✓ {ok_count} models succeeded")
print(f"✗ {error_count} models failed")
print(f"Results saved to {RESULTS_FILE}")
