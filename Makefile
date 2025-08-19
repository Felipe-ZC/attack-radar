run_signal-stream:
	podman compose up -d --build --no-cache --force-recreate signal-stream

run_signal-sweep:
	podman compose up -d --build --no-cache --force-recreate signal-sweep

clean:
	podman compose down
	rm -rf .venv __pycache__ *.egg-info
