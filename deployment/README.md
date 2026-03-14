# 部署文档说明

本目录包含所有与项目部署相关的文档和脚本。

## 目录结构

```
deployment/
├── README.md                        # 本文档
├── scripts/                        # 部署脚本
│   ├── start.sh                    # 本地启动脚本
│   └── cloudbaserc.json           # CloudBase 配置文件
├── docker/                         # Docker 相关
│   └── Dockerfile                  # Docker 镜像构建文件
└── docs/                           # 部署文档
    ├── CloudBase部署指南.md         # CloudBase 部署完整指南
    ├── CloudBase部署完成报告.md     # 部署完成状态报告
    ├── MTGCH API部署报告.md        # MTGCH API 部署说明
    ├── MTGCH API部署问题诊断.md    # 问题诊断与解决方案
    ├── MTGCH API最终部署报告.md    # 最终部署状态
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

# 或使用 MCP 工具部署
```

### Docker 部署

```bash
# 构建镜像
docker build -f deployment/docker/Dockerfile -t mtg-rules-api .

# 运行容器
docker run -p 80:80 mtg-rules-api
```

## 部署环境信息

### 当前 CloudBase 环境

- **环境 ID**: `magic-rules-assistant-0a1904c329`
- **函数名称**: `magic-rules-api`
- **运行时**: Python 3.10
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
| `/api/mtgch/search` | GET | MTGCH 卡牌搜索 |
| `/api/mtgch/card` | GET | MTGCH 单张卡牌 |
| `/api/mtgch/random` | GET | MTGCH 随机卡牌 |
| `/api/mtgch/autocomplete` | GET | MTGCH 自动补全 |

## 文档说明

### CloudBase部署指南.md
完整的 CloudBase 部署教程，包含：
- CloudBase CLI 安装
- 环境创建
- 云函数部署
- 微信公众号配置
- 测试验证

### CloudBase部署完成报告.md
当前部署状态报告，包含：
- 已完成的配置
- 访问地址
- 测试方法
- 故障排查

### MTGCH API部署报告.md
MTGCH API 集成说明，包含：
- 新增 API 端点
- 查询方式说明
- 本地测试结果

### MTGCH API部署问题诊断.md
部署过程中的问题与解决方案，包含：
- 函数类型不匹配问题
- 依赖缺失问题
- 路由未生效问题
- 多种解决方案

### MTGCH API最终部署报告.md
最终部署状态和待解决问题。

### MTGCH部署最终总结.md
MTGCH API 部署的总结文档。

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

### Dockerfile
Docker 镜像构建文件：
- 基于 Python 3.10 slim 镜像
- 安装项目依赖
- 复制代码和数据
- 配置运行参数

## 常见问题

### 1. 部署失败
- 检查环境 ID 是否正确
- 检查网络连接
- 查看 CloudBase 控制台日志

### 2. 微信验证失败
- 确认 URL 可访问
- 检查 Token 配置
- 确认消息加解密方式

### 3. MTGCH API 不工作
- 检查 requests 库是否安装
- 查看函数日志
- 参考 [MTGCH API部署问题诊断.md](docs/MTGCH API部署问题诊断.md)

## 相关链接

- [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
- [微信公众平台](https://mp.weixin.qq.com)
- [项目主 README](../README.md)
- [测试文档](../tests/README.md)
