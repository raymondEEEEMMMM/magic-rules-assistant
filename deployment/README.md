# 部署文档说明

本目录包含所有与项目部署相关的文档和脚本。

## 目录结构

```
deployment/
├── README.md                        # 本文档
├── scripts/                        # 部署脚本
│   ├── start.sh                    # 本地启动脚本
│   └── cloudbaserc.json           # CloudBase 配置文件
└── docs/                           # 部署文档
    ├── CloudBase部署指南.md         # CloudBase 部署完整指南
    ├── plan_openclaw_cloud.md     # OpenCLAW Gateway 部署方案
    ├── MTGCH API最终部署报告.md    # MTGCH API 部署报告
    └── MTGCH部署最终总结.md        # MTGCH 部署总结
```

## 快速开始

### 本地开发

```bash
# 使用启动脚本
bash deployment/scripts/start.sh

# 或手动启动
source venv/bin/activate
cd backend
python main.py
```

### CloudBase 部署

1. 参考 [CloudBase部署指南.md](docs/CloudBase部署指南.md)
2. 配置 `cloudbaserc.json` 中的环境 ID
3. 执行部署命令

```bash
# 部署云函数
tcb fn deploy magic-rules-api -e <env-id> --httpFn --yes
```

## 部署环境信息

### 当前 CloudBase 环境

- **环境 ID**: `magic-rules-assistant-0a1904c329`
- **函数名称**: `mtgAsk`
- **运行时**: Python 3.9
- **访问地址**: `https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com`

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/wechat` | GET | 微信服务器验证 |
| `/wechat` | POST | 微信消息接收 |
| `/api/search` | GET | 规则搜索 |
| `/api/keyword` | GET | 关键词查询 |
| `/api/card` | GET | 卡牌查询 |
| `/api/ai-judge/chat` | POST | AI 裁判问答 |
| `/api/ai-judge/analyze` | POST | 游戏局势分析 |

## AI 裁判部署

AI 裁判功能基于 OpenCLAW Gateway，部署在自建服务器上。

### 架构

```
微信小程序/公众号 → 云函数 mtgAsk → SSH + CLI → OpenCLAW Gateway (自建服务器)
                                                              ↓
                                                        ai_judge skill
                                                              ↓
                                                        MiniMax API
```

### 自建服务器配置

| 属性 | 值 |
|------|-----|
| 服务器 IP | 101.43.48.45 |
| SSH 端口 | 22 |
| Gateway 端口 | 18789 |

### 知识库同步

知识库存储在 `functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/`，与 GitHub 仓库完全对齐。

```bash
# 同步知识库到本地（从 GitHub）
python functions/mtgAsk/scripts/sync_judge_knowledge.py --rules --force

# 同步到服务器
python functions/mtgAsk/scripts/sync_judge_knowledge.py --skill
```

详见 [OpenCLAW Gateway 部署方案](docs/plan_openclaw_cloud.md)

## 文档说明

### CloudBase部署指南.md
完整的 CloudBase 部署教程，包含：
- CloudBase CLI 安装
- 环境创建
- 云函数部署
- 微信公众号配置
- 测试验证

### plan_openclaw_cloud.md
OpenCLAW Gateway 部署方案，包含：
- 自建服务器配置
- 知识库同步说明
- 环境变量配置

### MTGCH API最终部署报告.md
MTGCH API 集成说明，包含：
- 新增 API 端点
- 查询方式说明
- 本地测试结果

## 脚本说明

### start.sh
本地开发环境启动脚本，功能：
- 自动激活虚拟环境
- 检查并创建数据目录
- 初始化数据库（如果需要）
- 启动 API 服务

### cloudbaserc.json
CloudBase 配置文件，包含：
- 环境配置
- 函数配置
- 环境变量
- HTTP 访问路径

## 常见问题

### 1. 部署失败
- 检查环境 ID 是否正确
- 检查网络连接
- 查看 CloudBase 控制台日志

### 2. 微信验证失败
- 确认 URL 可访问
- 检查 Token 配置
- 确认消息加解密方式

### 3. AI 裁判不工作
- 检查 SSH 连接到服务器的配置
- 确认知识库是否同步
- 查看云函数日志

## 相关链接

- [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
- [微信公众平台](https://mp.weixin.qq.com)
- [项目主 README](../README.md)
- [测试文档](../tests/README.md)
