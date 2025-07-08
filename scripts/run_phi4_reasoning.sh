#!/bin/bash
#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LLAMA_BIN="$ROOT_DIR/llama.cpp/build/bin/llama-server"
MODEL_PATH="$ROOT_DIR/llama.cpp/models/phi-4-IQ4_XS.gguf"
LIB_PATH="$ROOT_DIR/llama.cpp/build/bin"

if pgrep -f "llama-server.*--port 8000" > /dev/null; then
    echo "Reasoning server is already running on port 8000."
    exit 1
fi

echo "Starting Phi-4-Reasoning server..."

LD_LIBRARY_PATH="$LIB_PATH:$LD_LIBRARY_PATH" \

CUDA_VISIBLE_DEVICES="-0" "$LLAMA_BIN" \
  --model "$MODEL_PATH" \
  --gpu-layers 41 \
  --host 0.0.0.0 \
  --port 8000 \
  --jinja
