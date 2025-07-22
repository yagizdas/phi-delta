#!/bin/bash
#!/bin/bash

if pgrep -f "vllm serve" > /dev/null; then
    echo "Multimodal server is already running."
    exit 1
fi

echo "Starting VLLM server..."

vllm serve microsoft/Phi-4-multimodal-instruct \
  --host 0.0.0.0 \
  --port 8002 \
  --trust-remote-code \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192

