# mtgAsk 部署方案

## 1. 部署架构

### 1.1 组件部署

| 组件 | 部署平台 | 配置 |
|-----|---------|------|
| 云函数 mtgAsk | 腾讯云 CloudBase | Python 3.10, 512MB, 300s timeout |
| MySQL 数据库 | 腾讯云 CloudBase MySQL | 外网地址: 27987 |
| OpenCLAW Gateway | 自建服务器 (Docker) | 1核 2GB, 端口 18789 |
| 微信小程序 | 微信小程序平台 | - |

### 1.2 访问拓扑

```
微信小程序 ──────► CloudBase 云函数 ──────► MySQL 数据库
                     │
                     │ SSH + CLI
                     ▼
              OpenCLAW Gateway ──────► MiniMax API
                     │
                     ▼
              Agent 容器 (per-user)
```

---

## 2. 部署前准备

### 2.1 环境要求

| 要求 | 说明 |
|-----|------|
| Node.js | 微信小程序开发 |
| Python 3.10+ | 本地测试和开发 |
| Docker | OpenCLAW Gateway 部署 |
| tcb CLI | 云函数部署 |

### 2.2 环境变量配置

**创建 `.env.local` 文件：**

```bash
# 微信配置
WECHAT_TOKEN=your_wechat_token

# MySQL 配置
MYSQL_HOST=sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com
MYSQL_PORT=27987
MYSQL_USER=mtingask
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=magic-rules-assistant-0a1904c329

# MiniMax API (AI 裁判)
MINIMAX_API_KEY=your_api_key

# OpenCLAW Gateway
OPENCLAW_ENABLED=true
OPENCLAW_HOST=your_server_ip
OPENCLAW_PORT=22
OPENCLAW_SSH_USER=openclaw
OPENCLAW_SSH_KEY_CONTENT=base64_encoded_private_key
OPENCLAW_AGENT=main
OPENCLAW_MAX_AGENTS=100
OPENCLAW_IDLE_TIMEOUT=30
```

### 2.3 依赖安装

```bash
# 本地虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r functions/mtgAsk/requirements.txt

# 云函数依赖 (Event 类型)
mkdir -p functions/mtgAsk/vendor
pip install --target functions/mtgAsk/vendor -r functions/mtgAsk/requirements.txt -q
```

---

## 3. CloudBase 云函数部署

### 3.1 部署命令

```bash
# 使用部署脚本
bash deploy.sh

# 或手动部署
tcb fn deploy mtgAsk --force
```

### 3.2 云函数配置

**文件：** `cloudbaserc.json`

```json
{
  "version": "2.0",
  "envId": "magic-rules-assistant-0a1904c329",
  "functionRoot": ".",
  "functions": [
    {
      "name": "mtgAsk",
      "timeout": 300,
      "runtime": "Python3.10",
      "handler": "index.main",
      "memorySize": 512,
      "envVariables": {}
    }
  ]
}
```

### 3.3 环境变量配置（CloudBase 控制台）

在 CloudBase 控制台设置以下环境变量：

| 变量 | 说明 |
|-----|------|
| `MYSQL_HOST` | MySQL 外网地址 |
| `MYSQL_PORT` | 27987 |
| `MYSQL_USER` | 数据库用户 |
| `MYSQL_PASSWORD` | 数据库密码 |
| `MYSQL_DATABASE` | 数据库名 |
| `WECHAT_TOKEN` | 微信验证 Token |
| `MINIMAX_API_KEY` | MiniMax API 密钥 |
| `OPENCLAW_ENABLED` | true |
| `OPENCLAW_HOST` | Gateway 服务器 IP |
| `OPENCLAW_SSH_KEY_CONTENT` | SSH 私钥（Base64） |

### 3.4 云函数入口

**文件：** `functions/mtgAsk/index.py`

简化版入口，通过路由分发请求：

```python
def main(event, context):
    # 路由处理
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    # ... 路由匹配和响应
```

---

## 4. OpenCLAW Gateway 部署

### 4.1 服务器要求

| 要求 | 配置 |
|-----|------|
| CPU | 1 核 |
| 内存 | 2 GB |
| 磁盘 | 20 GB |
| 操作系统 | Ubuntu 20.04+ |
| Docker | 20.10+ |
| 端口 | 22 (SSH), 18789 (Gateway) |

### 4.2 Docker 部署

**Dockerfile：** `cloudrun/openclaw-gateway/Dockerfile`

```dockerfile
FROM ubuntu:22.04

# 安装依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 OpenCLAW
RUN pip3 install openai anthropic

# 复制配置文件
COPY . /home/openclaw/

# 初始化工作目录
WORKDIR /home/openclaw

# 暴露端口
EXPOSE 18789

CMD ["python3", "-m", "openclaw", "gateway"]
```

**部署命令：**

```bash
tcb run:deprecated version create \
  -e magic-rules-assistant-0a1904c329 \
  -s openclaw-gateway \
  -p . \
  --dockerFile cloudrun/openclaw-gateway/Dockerfile \
  --port 18789 \
  -c 1 \
  --mem 2
```

### 4.3 Gateway 配置

**服务地址：** `https://openclaw-gateway-233331-7-1410769303.sh.run.tcloudbase.com`

**Agent 工作目录：** `/home/openclaw/agents/user_{sanitized_openid}`

---

## 5. 数据库初始化

### 5.1 创建数据库表

云函数首次启动时自动创建所需表：

```python
# ai_agent_pool 表
CREATE TABLE IF NOT EXISTS ai_agent_pool (
    id INT AUTO_INCREMENT PRIMARY KEY,
    openid VARCHAR(128) UNIQUE NOT NULL,
    agent_name VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_idle BOOLEAN DEFAULT FALSE,
    idle_since DATETIME,
    message_count INT DEFAULT 0
)

# ai_judge_daily_stats 表
CREATE TABLE IF NOT EXISTS ai_judge_daily_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    openid VARCHAR(128) NOT NULL,
    date DATE NOT NULL,
    question_count INT DEFAULT 0,
    UNIQUE KEY uk_openid_date (openid, date)
)

# decks 表
CREATE TABLE IF NOT EXISTS decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    openid VARCHAR(128) NOT NULL,
    name VARCHAR(255) NOT NULL,
    format VARCHAR(64) DEFAULT '其他',
    commander VARCHAR(255),
    cards TEXT,
    total_cards INT DEFAULT 0,
    avg_cmc VARCHAR(10) DEFAULT '0.00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### 5.2 规则数据导入

```bash
# 导入规则（通过 API 调用）
curl -X POST "https://your-function-url/api/rules/update" \
  -H "Content-Type: application/json"

# 或通过管理脚本
python functions/mtgAsk/backend/scripts/import_rules.py
```

---

## 6. 小程序配置

### 6.1 app.js 配置

**文件：** `miniprogram/app.js`

```javascript
App({
  globalData: {
    API_BASE_URL: 'https://your-function-url',
    // 云开发环境
    cloudEnv: 'your-env-id'
  }
})
```

### 6.2 云函数调用

```javascript
// 调用云函数
wx.cloud.callFunction({
  name: 'mtgAsk',
  data: {
    action: 'getOpenid'
  },
  success: res => {
    console.log(res.result.openid)
  }
})
```

---

## 7. 回滚方案

### 7.1 云函数回滚

```bash
# 查看历史版本
tcb run:deprecated version list -e magic-rules-assistant-0a1904c329 -s mtgAsk

# 回滚到指定版本
tcb run:deprecated version deploy \
  -e magic-rules-assistant-0a1904c329 \
  -s mtgAsk \
  -v version_id
```

### 7.2 数据库回滚

数据库无自动回滚，依赖 MySQL 备份：

1. 通过 CloudBase 控制台进行数据库备份
2. 恢复时选择指定备份点

### 7.3 OpenCLAW Gateway 回滚

```bash
# 查看历史版本
tcb run:deprecated version list -e magic-rules-assistant-0a1904c329 -s openclaw-gateway

# 回滚
tcb run:deprecated version deploy \
  -e magic-rules-assistant-0a1904c329 \
  -s openclaw-gateway \
  -v version_id
```

---

## 8. 监控与日志

### 8.1 云函数日志

**MCP 工具查询：**
```javascript
mcp__cloudbase__queryLogs({
  action: "searchLogs",
  service: "tcb",
  queryString: "error",
  limit: 20,
  sort: "desc"
})
```

**CloudBase 控制台：**
1. 登录 [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
2. 选择环境 > 云函数 > mtgAsk > 日志

### 8.2 AI 裁判日志

日志存储位置：
- 本地文件：`/tmp/logs/ai_judge_{date}.log`（云函数环境）
- MySQL 表：`ai_judge_logs`

### 8.3 健康检查

```bash
# 云函数健康检查
curl https://your-function-url/

# AI 裁判状态检查
curl -X POST https://your-function-url/api/ai-judge/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "status", "openid": ""}'
```

---

## 9. 故障排查

### 9.1 云函数调用失败

**检查项：**
1. 环境变量是否正确配置
2. MySQL 外网地址是否正确
3. 函数超时设置（建议 300s）

**日志查询：**
```bash
mcp__cloudbase__queryLogs({
  action: "searchLogs",
  service: "tcb",
  queryString: "Error",
  limit: 50
})
```

### 9.2 AI 裁判无响应

**检查项：**
1. OpenCLAW Gateway 是否运行
2. SSH 连接是否正常
3. MiniMax API 配额是否充足

**SSH 测试：**
```bash
curl -X POST https://your-function-url/api/test-ssh
```

### 9.3 数据库连接失败

**检查项：**
1. MySQL 外网地址是否正确
2. 防火墙是否开放 27987 端口
3. 用户权限是否正确

---

## 10. 部署检查清单

### 10.1 部署前检查

- [ ] 环境变量已配置
- [ ] 虚拟环境已创建并安装依赖
- [ ] 云函数 vendor 目录已生成
- [ ] MySQL 数据库已创建
- [ ] OpenCLAW Gateway 已部署

### 10.2 部署后验证

- [ ] 服务状态检查通过
- [ ] 卡牌搜索返回结果
- [ ] AI 裁判对话正常
- [ ] 套牌管理功能正常
- [ ] 日志正常记录

### 10.3 监控指标

| 指标 | 阈值 | 说明 |
|-----|------|------|
| 云函数错误率 | < 1% | 错误调用 / 总调用 |
| AI 响应时间 | < 30s | AI 裁判首次响应 |
| 数据库连接成功率 | > 99% | 数据库连接成功率 |

---

*文档版本: 1.0*
*最后更新: 2026-05-27*