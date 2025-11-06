#!/bin/bash
set -ex

cd /workspace

apt-get update && apt-get install -y curl

pip install --user huggingface-hub
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"

curl -fsSL https://ollama.com/install.sh | sh

nohup ollama serve > /workspace/ollama.log 2>&1 &

sleep 10

if [ ! -f "/workspace/models/ggml-model-Q5_K_M.gguf" ]; then
    hf download heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF ggml-model-Q5_K_M.gguf --local-dir /workspace/models
fi

if [ ! -f "/workspace/Modelfile" ]; then
    cat << 'EOT' > /workspace/Modelfile
FROM /workspace/models/ggml-model-Q5_K_M.gguf

TEMPLATE """{{- if .System }}
<s>{{ .System }}</s>
{{- end }}
<s>Human:
{{ .Prompt }}</s>
<s>Assistant:
"""

SYSTEM """A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions."""

PARAMETER stop <s>
PARAMETER stop </s>
EOT
fi

ollama create EEVE-Korean-10.8B -f /workspace/Modelfile

if ! grep -q "ollama run EEVE-Korean-10.8B" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "ollama run EEVE-Korean-10.8B" >> ~/.bashrc
fi

echo "---"
echo "Setup complete. Ollama server is running."
echo "Connect to the terminal to start chatting automatically."
echo "---"
sleep infinity