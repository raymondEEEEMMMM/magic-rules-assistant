#!/bin/bash
set -e

echo "Starting OpenCLAW Gateway..."

# Create .env file from template if it doesn't exist
if [ ! -f ~/.openclaw/.env ]; then
    echo "Creating .env file..."
    # Copy environment variables to .env
    if [ -n "$MINIMAX_API_KEY" ]; then
        echo "MINIMAX_API_KEY=$MINIMAX_API_KEY" >> ~/.openclaw/.env
    fi
    if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
        echo "OPENCLAW_GATEWAY_TOKEN=$OPENCLAW_GATEWAY_TOKEN" >> ~/.openclaw/.env
    fi
fi

# Run gateway
# The openclaw.json.template will be used
exec openclaw gateway run \
    --port 18789 \
    --bind 0.0.0.0 \
    --allow-unconfigured \
    --ws-log compact
