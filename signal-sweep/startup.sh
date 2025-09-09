#!/bin/bash

# Create cron job with environment variables
cat > /etc/cron.d/signal_sweep << EOF
REDIS_HOST=${REDIS_HOST}
REDIS_PORT=${REDIS_PORT}
${SWEEP_SCHEDULE} cd /app && /app/.venv/bin/python -m signal_sweep.main --config ./signal-sweep/data_sources.yml >> /var/log/cron.log 2>&1
EOF

# Set proper permissions
chmod 0644 /etc/cron.d/signal_sweep

# Apply cron job
crontab /etc/cron.d/signal_sweep

# Start cron and tail logs
cron && tail -f /var/log/cron.log
