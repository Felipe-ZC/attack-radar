install:
	uv pip install -e .

run: install 
	./.venv/bin/python -m src.signal_sweep.main --config ./data_sources.yml
