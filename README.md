# OpenRouter Models Speed Benchmark

A performance benchmark suite for testing LLM models via OpenRouter API. Measures latency, throughput, and time-to-first-token (TTFT).

## Features

- Tests multiple models from OpenRouter (Claude, GPT-4o, Llama, Mistral, Qwen, etc.)
- Measures TTFT (time to first token) and tokens/second
- Resume capability (continue from last completed model)
- Automatic rate limiting between requests
- Detailed results saved to JSON

## Setup

### 1. Get OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up and create an API key
3. Copy your API key

### 2. Set Environment Variable

**Option A: Create .env file** (recommended)
```bash
cp .env.example .env
# Then edit .env and add your API key
```

**Option B: PowerShell:**
```powershell
$env:OPENROUTER_API_KEY = "your-api-key-here"
```

**Option C: Command Prompt:**
```cmd
set OPENROUTER_API_KEY=your-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Start Fresh
```bash
python benchmark.py --restart
```

### Resume from Last Model
```bash
python benchmark.py
```
or
```bash
python benchmark.py --resume
```

## Models Included

- **Frontier Models**: GPT-4o, GPT-4 Turbo, Claude 3 Opus, Gemini Pro
- **High-Performance**: Llama 3.1 405B/70B, Mistral Large, Qwen Max
- **Cost-Effective**: Llama 3.1 8B, Claude 3 Sonnet, GPT-3.5 Turbo
- **Specialized**: Phind CodeLlama, OpenHermes, Perplexity Sonar

## Results

Results are automatically saved to `results.json` after each model completes. View the results using `visualize.html` or parse the JSON directly.

### Result Fields

- `id`: Model ID on OpenRouter
- `label`: Display name
- `status`: "ok" or "error"
- `total_time_s`: Total time for request (seconds)
- `tokens`: Number of tokens in response
- `tokens_per_second`: Throughput (tokens/sec)
- `ttft_s`: Time to first token (seconds)
- `response_preview`: First 100 chars of response

## Pricing

Visit [openrouter.ai/pricing](https://openrouter.ai/pricing) to see costs per 1M tokens for each model.

## Tips

- **Rate Limiting**: Default 12s wait between requests. Adjust `RATE_LIMIT_WAIT` if needed.
- **Timeout**: 60s per request. Adjust `REQUEST_TIMEOUT` for slower networks.
- **Resume**: The script automatically tracks completed models in `results.json`
