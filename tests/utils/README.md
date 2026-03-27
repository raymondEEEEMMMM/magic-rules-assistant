# 测试工具

本目录包含测试辅助工具和调试脚本。

## 工具文件

### test_path_debug.py

**功能**: 路径解析调试工具

**用途**:
- 调试 HTTP 请求路径解析
- 验证路径匹配逻辑
- 检查查询参数解析

**状态**: 默认跳过（需要外部网络）

**运行方式**:
```bash
pytest tests/utils/ -v
```

## 运行工具测试

```bash
# 运行路径调试测试（会被跳过）
pytest tests/utils/ -v

# 实际运行测试
pytest tests/utils/test_path_debug.py -v -m cloud
```

## pytest 标记

工具测试使用以下标记：

```python
@pytest.mark.cloud
@pytest.mark.api
@pytest.mark.skip(reason="需要外部网络连接")
def test_root_path(self):
    ...
```

## 扩展建议

可以添加更多调试工具：

- **test_env_debug.py**: 环境变量调试
- **test_db_debug.py**: 数据库连接调试
- **test_api_debug.py**: API 调用调试

---

**最后更新**: 2026-03-16
**测试框架**: pytest
