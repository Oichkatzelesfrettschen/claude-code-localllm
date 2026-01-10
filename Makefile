PYTHON ?= python3
OLLAMA_URL ?= http://127.0.0.1:11434/v1/chat/completions
OLLAMA_MODEL ?= llama3.1:latest
NPM_PACKAGE ?= @devcontainers/cli
NPM_VERSION ?= 0.80.3
NPM_TARBALL ?= /tmp/devcontainer-cli-0.80.3.tgz
VRAM_BENCH_CONFIG ?= tools/local_llm/probe_models.json

.PHONY: verify-devcontainer cost-model tool-probe policy-check policy-regression probe-suite probe-suite-candidates latency-probe runtime-probe vram-probe vram-bench router-config-validate

verify-devcontainer:
	curl -L -o "$(NPM_TARBALL)" "https://registry.npmjs.org/$(NPM_PACKAGE)/-/cli-$(NPM_VERSION).tgz"
	$(PYTHON) tools/supply_chain/verify_npm_integrity.py \
		--package "$(NPM_PACKAGE)" \
		--version "$(NPM_VERSION)" \
		--tarball "$(NPM_TARBALL)"

cost-model:
	$(PYTHON) tools/local_llm/cost_model.py --config tools/local_llm/scenarios.json

tool-probe:
	$(PYTHON) tools/local_llm/tool_call_probe.py \
		--url "$(OLLAMA_URL)" \
		--model "$(OLLAMA_MODEL)"

policy-check:
	$(PYTHON) tools/local_llm/policy_engine.py \
		--rules tools/local_llm/policy_rules.json \
		--paths README.md

policy-regression:
	$(PYTHON) tools/local_llm/policy_regression.py --fixtures tools/local_llm/policy_fixtures.json

probe-suite:
	$(PYTHON) tools/local_llm/probe_suite.py \
		--url "$(OLLAMA_URL)" \
		--config tools/local_llm/probe_models.json

probe-suite-candidates:
	$(PYTHON) tools/local_llm/probe_suite.py \
		--url "$(OLLAMA_URL)" \
		--config tools/local_llm/probe_models_candidates.json

latency-probe:
	$(PYTHON) tools/local_llm/latency_probe.py \
		--url "$(OLLAMA_URL)" \
		--model "$(OLLAMA_MODEL)"

runtime-probe:
	$(PYTHON) tools/local_llm/runtime_probe.py \
		--config tools/local_llm/runtime_matrix.json

vram-probe:
	$(PYTHON) tools/local_llm/vram_probe.py

vram-bench:
	$(PYTHON) tools/local_llm/vram_bench.py --url "$(OLLAMA_URL)" --config "$(VRAM_BENCH_CONFIG)"

router-config-validate:
	$(PYTHON) tools/local_llm/validate_router_config.py --path docs/examples/router-config.json
	$(PYTHON) tools/local_llm/validate_router_config.py --path docs/examples/router-config-openrouter.json
