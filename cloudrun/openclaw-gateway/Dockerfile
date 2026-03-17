# Docker build with environment variable support
FROM node:20-bookworm-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCLAW CLI globally
RUN npm install -g openclaw@latest

# Create openclaw user and set up directories
RUN useradd -m -s /bin/bash openclaw && \
    mkdir -p /home/openclaw/.openclaw/workspace/skills/ai_judge && \
    mkdir -p /home/openclaw/.openclaw/workspace/agent && \
    chown -R openclaw:openclaw /home/openclaw

# Copy ai_judge skill
COPY --chown=openclaw:openclaw workspace/skills/ai_judge/ /home/openclaw/.openclaw/workspace/skills/ai_judge/

# Copy configuration template
COPY --chown=openclaw:openclaw openclaw.json /home/openclaw/.openclaw/openclaw.json.template

# Create startup script
COPY --chown=openclaw:openclaw start.sh /home/openclaw/start.sh
RUN chmod +x /home/openclaw/start.sh

# Switch to openclaw user
USER openclaw

# Set working directory
WORKDIR /home/openclaw

# Expose ports (WebSocket)
EXPOSE 18789

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:18789/ || exit 1

# Start the gateway
CMD ["./start.sh"]
