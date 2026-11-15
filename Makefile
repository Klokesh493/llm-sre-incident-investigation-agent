PYTHON ?= python3
MODEL ?= qwen2.5:0.5b
PORT ?= 11434

.PHONY: verify demo live
verify:
	$(PYTHON) -B -m unittest discover -s tests -v
	$(PYTHON) -B agent.py evaluate

demo:
	$(PYTHON) -B agent.py run examples/main.json --replay examples/actions.json

live:
	$(PYTHON) -B agent.py run examples/main.json --model "$(MODEL)" --port "$(PORT)"
