FROM python:3.13

ARG SWEEP_SCHEDULE
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y cron
RUN pip install uv

# Copy application code
COPY . .

# Install data ingestion script dependencies
RUN uv sync
RUN uv pip install -e .

ENV PATH="/app/.venv/bin:$PATH"

# Copy startup script
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Create the log file
RUN touch /var/log/cron.log

# Use startup script
CMD ["/app/startup.sh"]
