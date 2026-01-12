PYTHON ?= python3
OLLAMA_URL ?= http://127.0.0.1:11434/v1/chat/completions
OLLAMA_MODEL ?= llama3.1:latest
LLAMACPP_URL ?= http://127.0.0.1:8081/v1/chat/completions
LLAMACPP_MODEL ?= local-gguf
NPM_PACKAGE ?= @devcontainers/cli
NPM_VERSION ?= 0.80.3
NPM_TARBALL ?= /tmp/devcontainer-cli-0.80.3.tgz
VRAM_BENCH_CONFIG ?= tools/local_llm/probe_models.json

.PHONY: verify-devcontainer cost-model json-lint openrouter-model-check gpu-runtime-guard ollama-preflight llamacpp-preflight tool-probe llamacpp-tool-probe policy-check policy-regression probe-suite probe-suite-candidates latency-probe runtime-probe runtime-probe-vllm vram-probe vram-bench router-config-validate failure-injection lint-python lint-shell lint typecheck test pre-commit-install pre-commit-run

verify-devcontainer:
	curl -L -o "$(NPM_TARBALL)" "https://registry.npmjs.org/$(NPM_PACKAGE)/-/cli-$(NPM_VERSION).tgz"
	$(PYTHON) tools/supply_chain/verify_npm_integrity.py \
		--package "$(NPM_PACKAGE)" \
		--version "$(NPM_VERSION)" \
		--tarball "$(NPM_TARBALL)"

cost-model:
	$(PYTHON) tools/local_llm/cost_model.py --config tools/local_llm/scenarios.json

json-lint:
	$(PYTHON) tools/local_llm/json_lint.py

openrouter-model-check:
	$(PYTHON) tools/local_llm/openrouter_model_check.py --config docs/examples/router-config-openrouter.json

gpu-runtime-guard:
	$(PYTHON) tools/local_llm/gpu_runtime_guard.py

ollama-preflight:
	@$(MAKE) gpu-runtime-guard
	@curl -fsS "http://127.0.0.1:11434/api/tags" >/dev/null && echo "OK: ollama server reachable" || (echo "ERROR: ollama server not reachable; run 'ollama serve'"; exit 1)

llamacpp-preflight:
	@curl -fsS "http://127.0.0.1:8081/v1/models" >/dev/null && echo "OK: llama.cpp OpenAI server reachable" || (echo "ERROR: llama.cpp server not reachable; start llama-server on 127.0.0.1:8081"; exit 1)

tool-probe:
	$(PYTHON) tools/local_llm/tool_call_probe.py \
		--url "$(OLLAMA_URL)" \
		--model "$(OLLAMA_MODEL)"

llamacpp-tool-probe:
	@$(MAKE) llamacpp-preflight
	$(PYTHON) tools/local_llm/llamacpp_tool_probe.py --url "$(LLAMACPP_URL)"

policy-check:
	$(PYTHON) tools/local_llm/policy_engine.py \
		--rules tools/local_llm/policy_rules.json \
		--paths README.md

policy-regression:
	$(PYTHON) tools/local_llm/policy_regression.py --fixtures tools/local_llm/policy_fixtures.json

probe-suite:
	@$(MAKE) ollama-preflight
	$(PYTHON) tools/local_llm/probe_suite.py \
		--url "$(OLLAMA_URL)" \
		--config tools/local_llm/probe_models.json

probe-suite-candidates:
	@$(MAKE) ollama-preflight
	$(PYTHON) tools/local_llm/probe_suite.py \
		--url "$(OLLAMA_URL)" \
		--config tools/local_llm/probe_models_candidates.json

latency-probe:
	@$(MAKE) ollama-preflight
	$(PYTHON) tools/local_llm/latency_probe.py \
		--url "$(OLLAMA_URL)" \
		--model "$(OLLAMA_MODEL)"

runtime-probe:
	@$(MAKE) ollama-preflight
	$(PYTHON) tools/local_llm/runtime_probe.py \
		--config tools/local_llm/runtime_matrix.json

runtime-probe-vllm:
	$(PYTHON) tools/local_llm/runtime_probe.py --config tools/local_llm/runtime_matrix_vllm_only.json

vram-probe:
	$(PYTHON) tools/local_llm/vram_probe.py

vram-bench:
	$(PYTHON) tools/local_llm/vram_bench.py --url "$(OLLAMA_URL)" --config "$(VRAM_BENCH_CONFIG)"

router-config-validate:
	$(PYTHON) tools/local_llm/validate_router_config.py --path docs/examples/router-config.json
	$(PYTHON) tools/local_llm/validate_router_config.py --path docs/examples/router-config-openrouter.json

failure-injection:
	$(PYTHON) tools/local_llm/failure_injection.py

# Static analysis and testing targets
lint-python:
	ruff check tools/local_llm/ plugins/hookify/ examples/
	ruff format --check tools/local_llm/ plugins/hookify/ examples/

lint-shell:
	shellcheck -S warning tools/local_llm/runtimes/*.sh .devcontainer/*.sh 2>/dev/null || true

lint: lint-python lint-shell json-lint

typecheck:
	mypy tools/local_llm/

test:
	pytest tests/

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
