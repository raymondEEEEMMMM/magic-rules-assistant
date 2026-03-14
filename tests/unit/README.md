# 单元测试

本目录用于存放单元测试文件。

## 待添加的单元测试

### test_config.py

测试配置管理模块

```python
def test_config_loading():
    """测试配置加载"""
    pass

def test_env_variables():
    """测试环境变量"""
    pass
```

### test_database.py

测试数据库操作

```python
def test_database_connection():
    """测试数据库连接"""
    pass

def test_rule_query():
    """测试规则查询"""
    pass

def test_card_query():
    """测试卡牌查询"""
    pass
```

### test_services.py

测试服务层逻辑

```python
def test_rule_service():
    """测试规则服务"""
    pass

def test_card_service():
    """测试卡牌服务"""
    pass

def test_mtgch_api_client():
    """测试MTGCH API客户端"""
    pass
```

## 创建新单元测试

1. 在本目录创建测试文件 `test_*.py`
2. 使用标准的测试框架（如 unittest 或 pytest）
3. 遵循命名规范：`test_函数名`
4. 添加清晰的文档字符串

## 运行单元测试

```bash
# 使用pytest（推荐）
pytest tests/unit/

# 使用unittest
python -m unittest discover tests/unit/

# 运行单个测试文件
python -m unittest tests/unit/test_config.py
```

## 单元测试规范

1. **独立性**: 每个测试应该独立运行
2. **可重复性**: 测试结果应该可以重复
3. **明确性**: 测试名称应该清晰描述测试内容
4. **快速性**: 单元测试应该快速执行

---

**最后更新**: 2026-03-13
**状态**: 待创建
