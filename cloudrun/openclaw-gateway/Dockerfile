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
    chown -R openclaw:openclaw /home/openclaw

# Copy skill files only (minimal set)
COPY --chown=openclaw:openclaw workspace/skills/ai_judge/SKILL.md /home/openclaw/.openclaw/workspace/skills/ai_judge/
COPY --chown=openclaw:openclaw workspace/skills/ai_judge/markdown /home/openclaw/.openclaw/workspace/skills/ai_judge/
COPY --chown=openclaw:openclaw workspace/skills/ai_judge/knowledge-map /home/openclaw/.openclaw/workspace/skills/ai_judge/

# Copy configuration
COPY --chown=openclaw:openclaw openclaw.json /home/openclaw/.openclaw/openclaw.json

# Copy startup script
COPY --chown=openclaw:openclaw start.sh /home/openclaw/start.sh
RUN chmod +x /home/openclaw/start.sh

# Switch to openclaw user
USER openclaw
WORKDIR /home/openclaw

# Expose port
EXPOSE 18789

# Start the gateway
CMD ["./start.sh"]
