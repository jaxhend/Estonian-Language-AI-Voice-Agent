#!/bin/bash
# ================================================================
# Run Gemma-3-27B model on 8×A100 with vLLM
# Requires Docker, NVIDIA Container Toolkit, and Hugging Face token.
# ================================================================

# Load Hugging Face token from environment or .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$HF_TOKEN" ]; then
  echo "❌ ERROR: HF_TOKEN not set. Please set it in your environment or .env file."
  exit 1
fi

# Optional: create cache dir if missing
mkdir -p /data/hf_cache

# Run container
docker run --gpus all --network host --ipc=host --ulimit memlock=-1 \
  -e HF_TOKEN="$HF_TOKEN" \
  -v /data/hf_cache:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model google/gemma-3-27b-it \
  --tensor-parallel-size 8 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --port 8000 \
  --host 0.0.0.0 \
  --disable-log-stats
