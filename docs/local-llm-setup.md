# Local LLM Setup (POC)

## 1) Start Ollama
```
ollama serve
```

## 2) Pull a Tool-Call Compliant Model
```
ollama pull llama3.1
ollama pull mistral
ollama pull qwen2.5:7b-instruct
```

## 3) Install claude-code-router
```
npm install -g @musistudio/claude-code-router
```

## 4) Configure the Router
Create `~/.claude-code-router/config.json` using the example in
`docs/examples/router-config.json` (defaults to `qwen2.5:7b-instruct`).
Set `ANTHROPIC_API_KEY` in your environment to enable the `think` route.

## 5) Start the Router
```
ccr start
ccr status
```

## 6) Validate Tool Calls
```
make tool-probe
make probe-suite
make runtime-probe
```

## Troubleshooting
- If tool calls fail, verify the model supports tool calls (`llama3.1` passes;
  `mistral` and `qwen2.5:7b-instruct` also pass; `qwen2.5-coder:7b` fails).
- If router fails to start, re-check `~/.claude-code-router/config.json`.

## Optional: vLLM Runtime (GPU)
After installing `python-vllm-cuda` or `vllama`, start a vLLM server and add it
to `tools/local_llm/runtime_matrix.json` (set `enabled: true`) before running:
```
make runtime-probe
```
