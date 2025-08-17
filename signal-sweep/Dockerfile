FROM python:3.11

WORKDIR /app

# Install dependencies
RUN pip install uv

# Copy application code
COPY . .

# Install data ingestion script dependencies
RUN uv sync

# Run the application
CMD ["uv", "run", "python", "-m", "src.signal_sweep.main", "--config", "./data_sources.yml"]
