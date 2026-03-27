# 集成测试

本目录包含集成测试，用于测试多个模块协同工作的功能。

## 测试文件

### test_first_stage.py

**功能**: 测试第一阶段完整功能

**测试内容**:
- 规则搜索功能
- 卡牌查询功能
- 关键词异能查询
- 问答模板

**状态**: 默认跳过（需要数据库环境）

### test_card_service.py

**功能**: 测试卡牌服务完整功能

**测试内容**:
- 卡牌名称搜索（模糊匹配）
- 关键词异能搜索
- 数据库统计功能
- 向量化数据准备

**状态**: 默认跳过（需要数据库环境）

### test_rule_downloader.py

**功能**: 测试规则下载和解析功能

**测试内容**:
- 规则下载（TXT 格式）
- 规则版本检查
- 规则内容解析
- 向量化数据准备

**状态**: 默认跳过（需要数据库环境）

## 运行测试

### 安装依赖

```bash
pip install pytest pytest-asyncio
```

### 运行集成测试

```bash
# 运行所有集成测试（会被跳过）
pytest tests/integration/ -v

# 如果有数据库环境，可以使用 -m 运行
pytest tests/integration/ -v -m integration
```

## pytest 标记

集成测试使用以下标记：

```python
# 默认跳过
pytestmark = pytest.mark.skip(reason="需要数据库环境")

# 或标记为 integration
@pytest.mark.integration
def test_database():
    ...
```

## 测试依赖

- Python 3.9+
- 已安装项目依赖
- 数据库已初始化
- 网络连接正常（部分测试需要）

---

**最后更新**: 2026-03-16
**测试框架**: pytest
