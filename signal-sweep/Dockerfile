FROM python:3.11

WORKDIR /app

# Install dependencies
RUN pip install uv

# Copy application code
COPY . .

RUN uv sync

# Run the application
CMD ["uv", "run", "python", "-m", "src.signal_sweep.main", "--config", "./data_sources.yml"]
