# 测试目录

本目录包含万智牌规则问答公众号项目的所有测试用例。

## 目录结构

```
tests/
├── README.md                    # 本文件
├── unit/                        # 单元测试（待创建）
│   ├── test_config.py
│   ├── test_database.py
│   └── test_services.py
├── integration/                 # 集成测试（待创建）
│   ├── test_api.py
│   └── test_wechat.py
├── cloud/                       # 云函数测试
│   └── test_cloud_mtgch_*.py    # CloudBase 云函数测试
└── utils/                       # 测试工具（待创建）
    └── test_helpers.py
```

## 测试文件说明

### 已有测试文件

| 文件名 | 类型 | 功能描述 | 状态 |
|--------|------|---------|------|
| `test_first_stage.py` | 功能测试 | 测试第一阶段功能（规则查询、卡牌查询） | ✅ 已完成 |
| `test_card_service.py` | 服务测试 | 测试卡牌服务（搜索、关键词、统计） | ✅ 已完成 |
| `test_mtgch_api.py` | API测试 | 测试MTGCH API客户端 | ✅ 已完成 |
| `test_rule_downloader.py` | 功能测试 | 测试规则下载功能 | ✅ 已完成 |
| `test_path_debug.py` | 调试测试 | 路径解析调试 | ✅ 已完成 |

### CloudBase云函数测试

| 文件名 | 类型 | 功能描述 | 状态 |
|--------|------|---------|------|
| `test_cloud_mtgch.py` | 云函数测试 | CloudBase云函数MTGCH API测试（v1） | ✅ 已完成 |
| `test_cloud_mtgch_correct.py` | 云函数测试 | CloudBase云函数MTGCH API测试（修正版） | ✅ 已完成 |
| `test_cloud_mtgch_v2.py` | 云函数测试 | CloudBase云函数MTGCH API测试（v2） | ✅ 已完成 |

## 快速开始

### 运行所有测试

```bash
# 进入项目根目录
cd /Users/lianghaoming/cbworkplace

# 激活虚拟环境（如果需要）
source venv/bin/activate

# 运行单个测试
python tests/test_first_stage.py

# 运行MTGCH API测试
python tests/test_mtgch_api.py

# 运行云函数测试
python tests/test_cloud_mtgch_correct.py
```

### 测试分类说明

#### 1. 基础功能测试

- **test_first_stage.py**: 测试基础规则查询和卡牌查询功能
- **test_card_service.py**: 测试卡牌服务完整功能
- **test_rule_downloader.py**: 测试规则下载和解析功能

#### 2. API集成测试

- **test_mtgch_api.py**: 测试MTGCH API客户端的所有功能
  - 卡牌搜索
  - 单张卡牌查询
  - 随机卡牌
  - 自动补全

#### 3. 云函数测试

- **test_cloud_mtgch.py**: 初版云函数测试
- **test_cloud_mtgch_correct.py**: 修正版云函数测试
- **test_cloud_mtgch_v2.py**: v2版云函数测试

#### 4. 调试工具

- **test_path_debug.py**: 路径解析调试工具

## 测试环境要求

### Python环境

- Python 3.10+
- 依赖包：见 `../requirements.txt`

### 环境变量

```bash
# 复制环境变量配置
cp backend/.env.example backend/.env

# 编辑配置（可选）
vim backend/.env
```

### 数据库

```bash
# 初始化数据库
python backend/init_data.py
```

## 测试数据

### 卡牌数据

测试使用的卡牌数据位于 `../data/` 目录：
- `magic_rules.db`: SQLite数据库文件
- 包含109,030+张卡牌

### 测试用卡牌

- 黑莲花 (Black Lotus)
- 闪电击 (Lightning Bolt)
- 森林 (Forest)
- 热忱骑士 (Knight of the White Orchid)

## 测试结果

### 第一阶段测试

```
✅ 规则搜索: 通过
✅ 卡牌查询: 通过
✅ 关键词异能: 通过
✅ 问答模板: 通过
```

### MTGCH API测试

```
✅ 卡牌搜索: 通过
✅ 单张卡牌: 通过
✅ 随机卡牌: 通过
✅ 自动补全: 通过
```

### 云函数测试

```
⚠️ HTTP访问: 部分完成（待解决路由匹配问题）
⚠️ 依赖安装: 待解决（requests库未自动安装）
```

## 测试最佳实践

1. **隔离性**: 每个测试应该独立运行，不依赖其他测试
2. **可重复性**: 测试结果应该可以重复执行
3. **明确性**: 测试失败时应该有清晰的错误信息
4. **覆盖性**: 测试应该覆盖主要功能和边界情况

## 常见问题

### Q: 测试失败怎么办？

A: 检查以下几点：
1. 是否激活了虚拟环境
2. 是否安装了所有依赖
3. 数据库是否已初始化
4. 环境变量是否配置正确

### Q: 如何添加新测试？

A: 
1. 在合适的子目录创建测试文件
2. 按照现有测试文件的格式编写
3. 在本README中更新测试说明
4. 运行测试确保通过

### Q: 云函数测试需要什么？

A: 
1. CloudBase CLI已安装
2. 已登录CloudBase账号
3. 云函数已部署
4. HTTP访问路径已配置

## 贡献指南

添加新测试时请遵循以下规范：

1. 测试文件命名：`test_*.py`
2. 使用清晰的函数命名
3. 添加必要的注释
4. 处理异常情况
5. 打印清晰的测试结果

## 相关文档

- [项目README](../README.md)
- [MTGCH API快速开始](../docs/MTGCH%20API快速开始.md)
- [MTGCH API接入说明](../docs/MTGCH%20API接入说明.md)
- [CloudBase部署指南](../docs/CloudBase部署指南.md)

---

**最后更新**: 2026-03-13
**维护者**: AI Assistant
