# 单元测试

本目录包含单元测试文件，使用 **pytest** 框架编写。

## 测试文件

### test_mtgch_api.py

MTGCH API 客户端单元测试，使用 mock 模拟网络请求。

**测试覆盖**:
- MTGCHAPIClient 类的所有方法
- format_card_info 格式化函数

**测试数量**: 27 个

**运行方式**:
```bash
pytest tests/unit/test_mtgch_api.py -v
```

## 测试结构

```python
# 使用 pytest fixture
@pytest.fixture
def mock_session():
    """创建 mock session"""
    with patch('services.mtgch_api.requests.Session') as mock:
        yield mock.return_value

# 测试类
class TestMTGCHAPIClient:
    """MTGCH API 客户端测试"""

    def test_search_cards_success(self, mock_session):
        """测试搜索卡牌成功"""
        ...

# 参数化测试
@pytest.mark.parametrize("rarity,expected", [
    ("C", "普通"),
    ("U", "非普通"),
])
def test_format_card_info_rarity_mapping(self, rarity, expected):
    """测试稀有度映射"""
    ...
```

## 添加新测试

1. 创建测试文件 `test_*.py`
2. 使用 pytest 格式
3. 使用 `@pytest.fixture` 管理测试资源
4. 使用 `@pytest.mark.parametrize` 进行参数化测试

## 运行测试

```bash
# 运行所有单元测试
pytest tests/unit/ -v

# 运行特定测试
pytest tests/unit/test_mtgch_api.py -v

# 显示详细输出
pytest tests/unit/ -vv

# 运行失败的测试
pytest tests/unit/ --lf
```

---

**最后更新**: 2026-03-16
**测试框架**: pytest
