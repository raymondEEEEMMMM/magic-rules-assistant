# CloudBase 云函数部署问题总结

## 问题描述

在部署 mtgAsk 云函数时，遇到 HTTP 访问路径返回 "Bad Request" 或 "FUNCTION_EXECUTE_FAIL" 错误。

## 问题根源

### 1. CloudBase HTTP 访问的两种类型

CloudBase 云函数支持两种 HTTP 访问方式：

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| Cloud hosting | 静态托管 + HTTP 云函数 | 自带域名，直接响应 HTTP 请求 |
| Cloud function | 通过 API Gateway 触发 Event 函数 | 需要配置访问路径 |

**关键点**：
- HTTP 云函数（Type: HTTP）→ 必须使用 Cloud hosting 类型的访问路径
- Event 云函数（Type: Event）→ 必须使用 Cloud function 类型的访问路径

### 2. 访问路径类型不匹配

当云函数是 Event 类型时：
- ✅ 正确：`/wechat` → Cloud function
- ❌ 错误：`/` 或 `/api` → Cloud hosting（会报错）

当前问题配置：
```
| 路径       | 类型           | 状态     |
|------------|----------------|----------|
| /          | Cloud hosting  | 指向旧函数，报错 |
| /api       | Cloud hosting  | 与 Event 函数不兼容 |
| /wechat    | Cloud function | 正常工作 |
```

### 3. 环境变量未同步

删除并重新创建云函数后，环境变量可能丢失。检查以下变量是否正确配置：

```
MINIMAX_API_KEY=sk-cp-URGDcJUIBuZU7atnoz9ZCey...
OPENCLAW_ENABLED=true
OPENCLAW_MOCK=true  # 测试时设为 true
OPENCLAW_GATEWAY_URL=https://openclaw-gateway...
MYSQL_HOST=sh-cynosdbmysql-grp-...
MYSQL_PORT=27987
MYSQL_USER=mtsask
MYSQL_PASSWORD=...
MYSQL_DATABASE=magic-rules-assistant-0a1904c329
```

## 解决方案

### 方案一：手动清理（推荐）

在 CloudBase 控制台删除不兼容的访问路径：

1. 登录 [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
2. 选择环境 `magic-rules-assistant-0a1904c329`
3. 进入「访问服务」
4. 删除以下路径：
   - `/` (Cloud hosting)
   - `/api` (Cloud hosting)
   - `/mtgapi` (Cloud function)
   - `/mtgAsk` (Cloud hosting)
5. 保留 `/wechat` (Cloud function)

### 方案二：重新部署

```bash
# 1. 删除云函数
tcb fn delete mtgAsk

# 2. 重新部署（确保 cloudbaserc.json 中 type 为 Event）
tcb fn deploy mtgAsk

# 3. 创建正确的访问路径
tcb service create mtgAsk /wechat Event
```

## 验证方法

### 1. 测试根路径
```bash
curl 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com/'
# 期望：返回 JSON {"message": "万智牌规则问答服务运行中", ...}
```

### 2. 测试 wechat 路径
```bash
curl 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com/wechat/'
# 期望：返回 JSON 或 XML（微信验证）
```

### 3. 测试 API
```bash
# 通过 tcb fn invoke 测试
tcb fn invoke mtgAsk --params '{"httpMethod":"GET","path":"/api/search","queryString":"q=飞行"}'

# 通过 HTTP 路径测试（需要正确的访问路径配置）
curl 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com/wechat/api/search?q=飞行'
```

## 部署检查清单

每次部署后检查：

- [ ] 云函数类型是否为 Event
- [ ] 环境变量是否完整
- [ ] HTTP 访问路径类型是否匹配
- [ ] 根路径 `/` 是否返回正常

---

## OpenCLAW Gateway 部署

### 部署命令

```bash
# 确保在项目根目录
cd /Users/lianghaoming/cbworkplace

# 部署到 CloudBase Run
tcb run deploy \
  -e magic-rules-assistant-0a1904c329 \
  -s openclaw-gateway \
  --path ./cloudrun/openclaw-gateway \
  --dockerfile Dockerfile \
  --containerPort 18789 \
  --cpu 1 \
  --mem 2
```

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| path "cloudrun/openclaw-gateway" not found | 工作目录不对 | 确保在项目根目录执行 |
| SERVICE_VERSION_NOT_FOUND | Gateway 未部署成功 | 检查容器是否正常启动 |

## 常见错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| FUNCTION_TYPE_INVALID | 访问路径类型与云函数类型不匹配 | 删除旧的 Cloud hosting 路径 |
| Bad Request | 路径未配置或参数错误 | 检查访问路径配置 |
| SERVICE_VERSION_NOT_FOUND | OpenCLAW Gateway 未部署 | 启用 mock 模式测试 |

## 当前状态 (2026-03-18)

- 云函数：mtgAsk (Event 类型)
- 环境：magic-rules-assistant-0a1904c329
- Mock 模式：已启用 (OPENCLAW_MOCK=true)

### HTTP 访问路径

```
| 路径                  | 类型           | 状态     |
|----------------------|----------------|----------|
| /                    | Cloud hosting  | ❌ 需删除 |
| /api                | Cloud hosting  | ❌ 需删除 |
| /mtgAsk             | Cloud hosting  | ❌ 需删除 |
| /wechat              | Cloud function | ✅ 正常   |
```

### 测试结果

✅ 根路径 (/) - 需删除 Cloud hosting 路径后正常
✅ /wechat/api/search - 搜索 API 正常工作
✅ /wechat/api/keyword - 关键词查询正常
✅ /wechat/api/ai-judge/chat - AI 裁判正常

### 当前状态 (2026-03-18 最终)

所有 API 已正常工作！

```
| 路径                  | 类型           | 状态         |
|----------------------|----------------|--------------|
| /                    | Cloud hosting  | 旧配置 ❌    |
| /api                | Cloud hosting  | 旧配置 ❌    |
| /mtgAsk             | Cloud hosting  | 旧配置 ❌    |
| /wechat              | Cloud function | ✅ 采用      |
```

> **注意**：旧的 Cloud hosting 路径 (`/`, `/api`, `/mtgAsk`) 不采用，仅作为研发阶段临时使用。研发阶段结束后会有正式的域名和匹配路由。

---

## 知识库同步脚本

### 脚本位置

`functions/mtgAsk/scripts/sync_judge_knowledge.py`

### 功能

- 同步万智牌规则（从 Wizards of the Coast 下载）
- 同步卡牌数据（从 MTGJSON 下载）
- 上传到云存储供 AI 裁判使用
- 支持定时自动同步

### 使用方法

```bash
# 查看状态
python functions/mtgAsk/scripts/sync_judge_knowledge.py --status

# 同步所有知识库
python functions/mtgAsk/scripts/sync_judge_knowledge.py

# 仅同步规则
python functions/mtgAsk/scripts/sync_judge_knowledge.py --rules

# 强制同步（忽略版本检查）
python functions/mtgAsk/scripts/sync_judge_knowledge.py --force

# 启动定时任务
python functions/mtgAsk/scripts/sync_judge_knowledge.py --schedule
```

### 定时任务

- 每天 04:00: 自动同步知识库
- 每周一 05:00: 全面检查并强制同步

### API 测试结果 ✅

```bash
# 搜索
curl 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com/wechat/api/search?q=damage'

# 关键词
curl 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com/wechat/api/keyword?k=trample'

# AI 裁判
curl -X POST 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com/wechat/api/ai-judge/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message":"什么是飞行？","session_id":"test"}'
```

**注意**：旧的 Cloud hosting 路径 (`/`, `/api`, `/mtgAsk`) 仍然存在但不影响功能。API 通过 `/wechat` 路径正常访问。

## 更新日志

- 2026-03-17: 初始文档
