# OpenCLAW Gateway 部署方案

## 背景
- 云函数 mtgAsk 需要调用 OpenCLAW 进行万智牌规则问答
- OpenCLAW Gateway 部署在自建服务器上（不再使用 CloudBase Run）
- 知识库通过同步脚本从 GitHub 同步

## 当前部署架构

```
微信小程序/公众号 → 云函数 mtgAsk (CloudBase) → SSH + CLI → OpenCLAW Gateway (自建服务器)
                                                              ↓
                                                        ai_judge skill
                                                              ↓
                                                        MiniMax API
```

## 自建服务器配置

| 属性 | 值 |
|------|-----|
| 服务器 IP | 101.43.48.45 |
| SSH 端口 | 22 |
| SSH 用户 | root |
| Gateway 端口 | 18789 |
| 技能目录 | /root/openclaw/workspace/skills/ai_judge |

## 知识库同步

### 同步流程

```
GitHub (Kuuusoda/magic-comp-rules-zh-cn-agent)
        ↓
同步脚本 (sync_judge_knowledge.py)
        ↓
本地目录 (functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/)
        ↓
同步脚本 --skill
        ↓
服务器 (/root/openclaw/workspace/skills/ai_judge/)
```

### 同步命令

```bash
# 同步知识库到本地
python functions/mtgAsk/scripts/sync_judge_knowledge.py --rules --force

# 同步到服务器
python functions/mtgAsk/scripts/sync_judge_knowledge.py --skill
```

### 同步的文件

| 目录 | 说明 |
|------|------|
| `markdown/` | 规则 1-9 章 + 术语表 |
| `references/` | 知识图谱 |
| `skill.md` | 技能定义 |
| `345.md` | 裁判技能配置 |

## 云函数配置

### 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|-------|
| OPENCLAW_ENABLED | 启用 OpenCLAW | true |
| OPENCLAW_HOST | 服务器 IP | 101.43.48.45 |
| OPENCLAW_PORT | SSH 端口 | 22 |
| OPENCLAW_SSH_USER | SSH 用户名 | root |
| OPENCLAW_SSH_PASSWORD | SSH 密码 | - |
| OPENCLAW_AGENT | Agent 名称 | main |

### API 端点

| 端点 | 方法 | 功能 |
|-----|------|------|
| `/api/ai-judge/chat` | POST | AI 裁判问答 |
| `/api/ai-judge/analyze` | POST | 游戏局势分析 |
| `/api/ai-judge/clear` | POST | 清除会话 |

## 关键文件

| 文件 | 说明 |
|------|------|
| `functions/mtgAsk/backend/services/ai_judge_service.py` | AI 裁判服务 |
| `functions/mtgAsk/scripts/sync_judge_knowledge.py` | 同步脚本 |
| `functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/` | 本地知识库 |

## 验证方式

1. 测试 API 调用：
```bash
curl -X POST https://<mtgask-url>/api/ai-judge/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"闪电击的伤害何时结算？"}'
```

2. 检查服务器知识库：
```bash
ssh root@101.43.48.45 "ls -la /root/openclaw/workspace/skills/ai_judge/"
```
