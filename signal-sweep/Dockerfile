FROM python:3.11

ARG SWEEP_SCHEDULE

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y cron
RUN pip install uv

# Copy application code
COPY . .

# Install data ingestion script dependencies
RUN uv sync

# Create new cron job
RUN echo "${SWEEP_SCHEDULE} cd /app && /usr/local/bin/uv run python -m src.signal_sweep.main --config ./data_sources.yml >> /var/log/cron.log 2>&1" > /etc/cron.d/signal_sweep

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/signal_sweep

# Apply cron job
RUN crontab /etc/cron.d/signal_sweep

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start cron and your application
CMD cron && tail -f /var/log/cron.log
