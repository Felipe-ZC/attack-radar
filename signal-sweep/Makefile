install:
	uv pip install -e .

install-tests:
	uv sync --group test

run-tests:
	uv run pytest .

run: install 
	./.venv/bin/python -m src.signal_sweep.main --config ./data_sources.yml
