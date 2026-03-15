# 部署文档

本目录包含项目部署相关的文档和脚本。

## 目录结构

```
deployment/
├── README.md              # 本文档
├── scripts/              # 部署脚本
│   ├── start.sh         # 本地启动脚本
│   └── cloudbaserc.json # CloudBase 配置
├── docker/               # Docker 相关
│   └── Dockerfile        # Docker 镜像构建文件
└── docs/                 # 部署文档
    ├── 云函数部署指南.md  # 云函数部署 (推荐)
    ├── 部署架构.md       # 部署架构说明
    └── 云端API部署完整指南.md # 完整部署指南
```

## 快速开始

### 本地开发

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python functions/mtgAsk/backend/main.py
```

服务运行在 `http://localhost:8000`

### CloudBase 云函数部署

推荐使用**事件云函数**，步骤：

1. **删除旧函数**（如需重建）
2. **创建新函数**
3. **测试调用**

详细步骤见 [云函数部署指南.md](docs/云函数部署指南.md)

### Docker 部署

```bash
# 构建镜像
docker build -t mtg-ask-api .

# 运行容器
docker run -p 3000:3000 mtg-ask-api
```

## 环境信息

- **环境 ID**: `magic-rules-assistant-0a1904c329`
- **云函数**: `mtgAsk` (Event 类型, Python 3.10)
- **数据库外网地址**: `sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com:27987`

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/api/search` | GET | 规则搜索 |
| `/api/keyword` | GET | 关键词查询 |
| `/api/card` | GET | 卡牌查询 |

## 常见问题

1. **云函数无法连接数据库**: 确保使用外网地址，内网地址云函数无法访问
2. **scf_bootstrap 错误**: 事件云函数不需要 bootstrap
3. **Runtime 不支持修改**: 删除重建函数
