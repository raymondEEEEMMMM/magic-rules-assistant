# mtgAsk - 万智牌规则问答系统

## 项目简介
基于微信公众平台的万智牌规则智能问答系统，帮助牌手快速查询和理解万智牌规则。未来将扩展 AI 裁判、咨询更新等更多功能。

## ✅ 已完成功能

### 第一阶段
- ✅ 基础关键词规则查询
- ✅ 卡牌名 → 规则文本
- ✅ 简单问答模板库
- ✅ 基础菜单结构

### 规则下载功能
- ✅ 自动下载最新规则（TXT格式）
- ✅ 规则版本检查和增量更新
- ✅ 规则内容解析（1133条规则、190个关键词）
- ✅ 定时任务调度（每天03:00、每周一10:00）
- ✅ 向量化数据准备

### 卡牌数据集成
- ✅ MTGSQLite 数据库下载（109,030+ 张卡牌）
- ✅ 卡牌名称搜索（模糊匹配）
- ✅ 关键词异能搜索（216个关键词）
- ✅ 向量化数据准备
- ✅ 数据库统计功能

## 📦 技术栈
- 后端: Python + FastAPI
- 数据库: SQLite
- AI问答: OpenAI API (第二阶段)
- 部署: 待定

## 🏗️ 项目结构
```
cbworkplace/
├── mtgAsk/              # 云函数后端
│   ├── backend/         # 后端服务
│   │   ├── config.py   # 配置管理
│   │   ├── database.py # 数据库操作
│   │   ├── routes.py   # API路由
│   │   ├── main.py     # 服务入口
│   │   ├── services/   # 业务逻辑
│   │   └── wechat/     # 微信相关
│   ├── data/           # 数据目录
│   │   └── magic_rules.db  # 规则数据库
│   └── index.py        # 云函数入口
├── miniprogram/         # 微信小程序
├── docs/                # 文档
├── tests/               # 测试目录
├── deployment/         # 部署相关
├── start.sh            # 启动脚本
├── requirements.txt    # 依赖列表
└── README.md
```

## 🚀 快速开始

### 1. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 2. 安装依赖
```bash
# 使用虚拟环境（推荐）
pip install -r requirements.txt

# 或使用系统 Python
pip3 install -r requirements.txt
```

### 3. 配置环境变量
复制 `backend/.env.example` 为 `backend/.env`，并根据需要修改配置。

### 4. 初始化数据库
```bash
python backend/init_data.py
```

### 5. 启动服务
```bash
# 方式一：使用启动脚本（自动激活虚拟环境）
bash deployment/scripts/start.sh

# 方式二：手动启动
source venv/bin/activate  # 激活虚拟环境
python backend/main.py
```

### 6. 测试功能
```bash
# 运行测试脚本（查看tests/目录获取完整列表）
python tests/integration/test_first_stage.py

# 测试卡牌查询
python tests/integration/test_card_service.py

# 测试MTGCH API
python tests/integration/test_mtgch_api.py

# 测试云函数
python tests/cloud/test_cloud_mtgch_correct.py

# 或测试 API 端点
curl 'http://localhost:8000/api/search?q=飞行'
curl 'http://localhost:8000/api/card?n=黑莲花'
curl 'http://localhost:8000/api/keyword?k=践踏'
```

详见 [测试文档](./tests/README.md)

## 📡 API 端点

### 公开端点
- `GET /` - 服务状态检查
- `GET /docs` - Swagger API 文档
- `GET /wechat` - 微信服务器验证
- `POST /wechat` - 微信消息接收

### 调试端点
- `GET /api/search?q=` - 规则综合搜索
- `GET /api/keyword?k=` - 关键词异能查询
- `GET /api/card?n=` - 卡牌规则查询

### 规则管理端点
- `POST /api/rules/update` - 更新规则（可选force参数）
- `GET /api/rules/parse` - 解析规则文件
- `GET /api/rules/vectorization` - 获取向量化数据
- `GET /api/rules/status` - 获取规则状态

### 卡牌数据端点（开发中）
- `GET /api/cards/search?name=` - 搜索卡牌
- `GET /api/cards/keywords?list=` - 按关键词搜索
- `GET /api/cards/keywords/list` - 获取所有关键词
- `GET /api/cards/stats` - 获取数据库统计

## 💬 用户交互示例

```
用户: 飞行
系统: 📌 飞行
      具有飞行异能的生物不能被不具有飞行异能的生物阻挡。

      完整规则:
      702.9. 飞行
      702.9a 飞行是一种静态异能，影响生物进行阻挡的方式。
      ...

用户: 卡牌:黑莲花
系统: 🎴 黑莲花
      类型: 神器
      规则文本: 牺牲黑莲花：加三点任意颜色的法术力。

用户: 异能:践踏
系统: 📌 践踏
      具有践踏异能的生物在战斗时，超额的伤害会分配给防御牌手...

用户: /help
系统: 🃏 万智牌规则助手使用指南
      【基础功能】
      • 直接输入问题: 我会搜索相关规则
      ...
```

## 📊 数据库说明

### 预置数据
- **关键词异能**: 7个（飞行、践踏、先攻、闪现、辟邪、死触、系命）
- **卡牌**: 5张（黑莲花、安塔卡的命令、闪电击、森林、热忱骑士）
- **问答模板**: 8个（堆栈、优先权、回合结构等）
- **规则条目**: 2个（基础规则示例）

### 数据表结构
- `rules` - 综合规则表
- `keyword_abilities` - 关键词异能表
- `card_rules` - 卡牌规则表
- `qa_templates` - 问答模板表

## 🔧 配置微信公众号

1. 在微信公众平台申请服务号/订阅号
2. 获取 AppID、AppSecret、Token
3. 在 `backend/.env` 中配置相关参数
4. 在公众平台设置服务器 URL 和 Token
5. 开启服务器配置

## 📖 下一步计划

### 第二阶段
- [ ] AI 智能问答接入
- [ ] 复杂场景分析
- [ ] 每日一题功能
- [ ] 用户提问系统

### 技术优化
- [ ] 添加中文分词
- [ ] 优化搜索算法
- [ ] 添加缓存机制
- [ ] 日志系统
- [ ] 单元测试

## 📝 许可证
MIT License
