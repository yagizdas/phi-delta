#!/bin/bash
#!/bin/bash

# You do not need to change this path
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LLAMA_BIN="$ROOT_DIR/llama.cpp/build/bin/llama-server"

# Change this to the path where your models are stored, can be changed to any GGUF model
# For Phi-4, you can use one of the following model, S_MODEL is recommended.
XS_MODEL_PATH="$ROOT_DIR/llama.cpp/models/phi-4-IQ4_XS.gguf"
S_MODEL_PATH="$ROOT_DIR/llama.cpp/models/phi-4-Q4_K_S.gguf"

# Change this to the path where your llama.cpp is stored
LIB_PATH="$ROOT_DIR/llama.cpp/build/bin"

if pgrep -f "llama-server.*--port 8000" > /dev/null; then
    echo "Reasoning server is already running on port 8000."
    exit 1
fi

echo "Starting Phi-4-Reasoning server..."

LD_LIBRARY_PATH="$LIB_PATH:$LD_LIBRARY_PATH" \

# GPU Layers 
CUDA_VISIBLE_DEVICES="-0" "$LLAMA_BIN" \
  --model "$S_MODEL_PATH" \
  --gpu-layers 41 \
  --host 0.0.0.0 \
  --port 8000 \
  --jinja
