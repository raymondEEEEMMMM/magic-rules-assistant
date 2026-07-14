---
name: openclaw
description: OpenCLAW Gateway management - agent lifecycle, model configuration, gateway control, skills, and sandbox management. Server: 101.43.48.45:22, Gateway port: 18789. Official docs: https://docs.openclaw.ai/
---

## Connection

SSH: `sshpass -p 'Ray1994@' ssh -o StrictHostKeyChecking=no openclaw@101.43.48.45`

Binary: `/usr/local/bin/openclaw`

Gateway health: `curl -s http://localhost:18789/health`

Config file: `/home/openclaw/.openclaw/openclaw.json`

## Gateway Management

```bash
# Restart gateway (systemd user service)
sshpass -p 'Ray1994@' ssh -o StrictHostKeyChecking=no openclaw@101.43.48.45 "systemctl --user restart openclaw-gateway"

# Or send HUP signal
sshpass -p 'Ray1994@' ssh -o StrictHostKeyChecking=no openclaw@101.43.48.45 "pkill -HUP -f openclaw-gateway && sleep 3 && cd /home/openclaw && nohup openclaw gateway >> /tmp/gateway.log 2>&1 &"

# Check health
curl -s http://localhost:18789/health

# Gateway status
openclaw gateway status

# Gateway run (foreground)
openclaw gateway run

# Gateway restart via CLI
openclaw gateway restart

# View logs
openclaw logs --tail 50
```

## Agent Management

```bash
# List all agents
openclaw agents list
openclaw agents list --json
openclaw agents list --bindings

# Add new agent
openclaw agents add <name> --workspace /home/openclaw/agents/<name>

# Delete agent
openclaw agents delete <agent-id>

# Set agent identity
openclaw agents set-identity <agent-id> --name "Agent Name"

# Check agent workspace
cat /home/openclaw/agents/<agent-id>/SOUL.md
```

## Model Configuration

```bash
# List available models
openclaw models list

# Check model status
openclaw models status

# Set default model (format: provider/modelId)
openclaw models set minimax-cn/MiniMax-M2.7

# Model fallbacks
openclaw models fallbacks list
openclaw models fallbacks add minimax-cn/MiniMax-M2.5

# Model aliases
openclaw models aliases list
```

## Config Management

```bash
# View full config
cat /home/openclaw/.openclaw/openclaw.json

# Get config value (dot path)
openclaw config get agents.defaults.model.primary

# Set config value
openclaw config set agents.defaults.model.primary "minimax-cn/MiniMax-M2.7"

# Validate config
openclaw config validate

# Config file path
openclaw config file
```

## Skills (ClawHub)

```bash
# List available skills
openclaw skills list

# Check skill setup status
openclaw skills check

# Search ClawHub
openclaw skills search <query>

# Install skill from ClawHub
openclaw skills install <slug>

# Update installed skills
openclaw skills update
```

## Sandbox Management

```bash
# List sandbox containers
openclaw sandbox list

# Recreate all containers
openclaw sandbox recreate --all

# Recreate specific session
openclaw sandbox recreate --session <session-id>

# Recreate agent containers
openclaw sandbox recreate --agent <agent-id>

# Explain sandbox policy
openclaw sandbox explain
```

## Quick Reference

| Action | Command |
|--------|---------|
| Restart gateway | `systemctl --user restart openclaw-gateway` |
| Check health | `curl -s http://localhost:18789/health` |
| List agents | `openclaw agents list --json` |
| Add agent | `openclaw agents add <name> --workspace /home/openclaw/agents/<name>` |
| Delete agent | `openclaw agents delete <agent-id>` |
| Set model | `openclaw models set <provider/model>` |
| List models | `openclaw models list` |
| View config | `cat /home/openclaw/.openclaw/openclaw.json` |
| List skills | `openclaw skills list` |
| Sandbox list | `openclaw sandbox list` |

## Config Structure (openclaw.json)

Key paths:
- `agents.defaults.model.primary` - Default model (e.g., `minimax-cn/MiniMax-M2.7`)
- `agents.defaults.model.fallbacks` - Fallback models array
- `models.providers` - Model provider configurations
- `gateway.port` - Gateway port (default 18789)
- `gateway.auth.token` - Gateway auth token
