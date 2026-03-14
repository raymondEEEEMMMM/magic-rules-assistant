# 测试工具

本目录包含测试辅助工具和调试脚本。

## 工具文件

### test_path_debug.py

**功能**: 路径解析调试工具

**用途**:
- 调试HTTP请求路径解析
- 验证路径匹配逻辑
- 检查查询参数解析

**运行方式**:
```bash
python tests/utils/test_path_debug.py
```

## 使用场景

### 调试HTTP请求

当遇到路径匹配问题时，可以运行此工具：

```bash
# 运行路径调试工具
python tests/utils/test_path_debug.py

# 观察输出，检查路径是否正确解析
```

### 验证路由逻辑

检查云函数中的路由逻辑是否正确：

```python
# 查看路径解析结果
print(f"Parsed path: {path}")
print(f"Query params: {query_params}")
```

## 输出示例

```
=== Path Debug Test ===
Full path: /api/mtgch/search?q=Lightning&page_size=1
Parsed path: /api/mtgch/search
Query params: {'q': 'Lightning', 'page_size': '1'}
Path type: MTGCH Search API
```

## 注意事项

1. 此工具仅用于调试，不影响生产环境
2. 运行时需要在项目根目录
3. 需要激活虚拟环境（如已创建）

## 扩展建议

可以添加更多调试工具：

- **test_env_debug.py**: 环境变量调试
- **test_db_debug.py**: 数据库连接调试
- **test_api_debug.py**: API调用调试
- **test_network_debug.py**: 网络连接调试

---

**最后更新**: 2026-03-13
