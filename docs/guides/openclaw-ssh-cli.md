# OpenCLAW SSH + CLI 调用指南

## 概述

OpenCLAW Gateway 部署在自建服务器上，通过 SSH + CLI 方式调用。

## 调用架构

```
mtgAsk 云函数 → SSH + paramiko → 自建服务器 (101.43.48.45)
                                            ↓
                                      openclaw CLI
                                            ↓
                                      ai_judge skill
                                            ↓
                                      MiniMax API
```

## 命令格式

### 基础命令

```bash
openclaw agent --agent <agent_name> -m "<message>" [--json]
```

### 参数说明

| 参数 | 简写 | 说明 | 必需 |
|------|------|------|------|
| `--agent` | - | Agent 名称 | 是 |
| `-m` | --message | 用户消息/问题 | 是 |
| `--json` | - | 返回 JSON 格式 | 否 |

### 完整示例

```bash
# 文本响应
openclaw agent --agent main -m "闪电击的伤害何时结算？"

# JSON 响应
openclaw agent --agent main -m "闪电击的伤害何时结算？" --json
```

## SSH 调用方式

### 直接 SSH 执行

```bash
ssh openclaw@$OPENCLAW_HOST "bash -i -c 'openclaw agent --agent main -m \"闪电击的伤害何时结算？\" --json'"
```

### 通过 Python paramiko

```python
import paramiko
from io import StringIO

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 使用私钥内容连接
key_content = os.getenv("OPENCLAW_SSH_KEY_CONTENT", "")
pkey = paramiko.PKey.from_private_key(StringIO(key_content))
client.connect(os.getenv("OPENCLAW_HOST"), port=22, username="openclaw", pkey=pkey)

cmd = 'bash -i -c "openclaw agent --agent main -m \"闪电击的伤害何时结算？\" --json"'
stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
output = stdout.read().decode()
client.close()
```

## 响应格式

### JSON 响应结构

```json
{
  "status": "ok",
  "result": {
    "payloads": [
      {
        "type": "text",
        "text": "AI 回答内容..."
      }
    ]
  }
}
```

### 错误响应

```json
{
  "status": "error",
  "message": "错误信息"
}
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENCLAW_ENABLED` | 启用开关 | true |
| `OPENCLAW_HOST` | 服务器地址 | (环境变量) |
| `OPENCLAW_PORT` | SSH 端口 | 22 |
| `OPENCLAW_SSH_USER` | SSH 用户名 | openclaw |
| `OPENCLAW_SSH_KEY` | SSH 私钥/内容 | - |
| `OPENCLAW_SSH_KEY_CONTENT` | SSH 私钥内容 | - |
| `OPENCLAW_AGENT` | Agent 名称 | main |

### 服务器配置

| 属性 | 值 |
|------|-----|
| 服务器 IP | (环境变量 OPENCLAW_HOST) |
| SSH 端口 | 22 |
| SSH 用户 | openclaw |
| Gateway 端口 | 18789 |
| Agent 目录 | /home/openclaw/agents/ |

## Python 客户端

### 使用 OpenCLAWClient

```python
from backend.services.openclaw_client import OpenCLAWClient

# 创建客户端
client = OpenCLAWClient(
    host=os.getenv("OPENCLAW_HOST", "101.43.48.45"),
    port=22,
    username="openclaw",
    agent="main"
)

# 调用 agent（返回文本）
result = client.call_agent("闪电击的伤害何时结算？")
print(result)

# 调用 agent（返回 JSON）
result = client.call_agent_json("闪电击的伤害何时结算？")
print(result["text"])

# 关闭连接
client.close()
```

### 使用上下文管理器

```python
from backend.services.openclaw_client import OpenCLAWClient

with OpenCLAWClient() as client:
    result = client.call_agent("问题")
    print(result)
```

### 使用便捷函数

```python
from backend.services.openclaw_client import call_openclaw

# 快速调用
result = call_openclaw("闪电击的伤害何时结算？")
```

## 错误处理

```python
from backend.services.openclaw_client import OpenCLAWClient

client = OpenCLAWClient()

result = client.call_agent_json("问题")
if result.get("status") == "ok":
    print(result["text"])
else:
    print(f"错误: {result.get('message')}")
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `backend/services/openclaw_client.py` | Python 客户端实现 |
| `backend/services/ai_judge_service.py` | AI 裁判服务（使用此客户端） |
| `scripts/sync_judge_knowledge.py` | 知识库同步脚本 |
