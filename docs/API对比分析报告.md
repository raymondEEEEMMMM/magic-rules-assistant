# API 对比分析报告

## 测试时间
2026-03-13

## 测试目的
对比本地和云端 API 返回值，识别和解决差异问题。

## 测试端点
`/api/keyword?k=飞行`

## 问题发现

### 核心问题

云端 API 返回的是默认响应，而不是预期的 API 结果。

### 对比结果

#### 本地返回（正确）

```json
{
  "keyword": "飞行",
  "result": {
    "keyword_name": "飞行",
    "description": "具有飞行异能的生物不能被不具有飞行异能的生物阻挡。",
    "full_text": "702.9. 飞行\n702.9a 飞行是一种静态异能，影响生物进行阻挡的方式。\n702.9b 具有飞行异能的生物不能被不具有飞行异能的生物阻挡。具有飞行异能的生物可以阻挡不具有飞行异能的生物，反之亦然。\n702.9c 具有飞行异能的生物可以阻挡具有飞行异能的生物。\n702.9d 飞行的多个实例之间无交互。",
    "examples": [
      "天空督军具有飞行，不能被普通地面生物阻挡",
      "如果生物失去了飞行，它就可以被普通地面生物阻挡"
    ]
  }
}
```

#### 云端返回（错误）

```json
{
  "message": "万智牌规则问答服务运行中",
  "status": "ok",
  "service": "CloudBase HTTP Function",
  "path": "/keyword",
  "query_params": {
    "k": "飞行"
  }
}
```

## 问题分析

### 路径不匹配

| 项目 | 本地 | 云端 |
|------|------|------|
| 请求路径 | `/api/keyword` | `/api/keyword` |
| 函数接收路径 | N/A | `/keyword` |
| 函数期望路径 | N/A | `/api/keyword` |
| 匹配结果 | N/A | ❌ 不匹配 |

### 根本原因

CloudBase HTTP 访问配置可能在转发请求时去掉了 `/api` 前缀，导致：

1. **请求**: `/api/keyword?k=飞行`
2. **CloudBase 网关处理**: 去掉 `/api` 前缀 → `/keyword?k=飞行`
3. **函数接收**: `/keyword`
4. **路由匹配**: 函数只匹配 `/api/keyword`，不匹配 `/keyword`
5. **结果**: 走默认路由，返回服务状态

### 证据

从云端返回的 `path` 字段可以看到：
```json
{
  "path": "/keyword",
  "query_params": {"k": "飞行"}
}
```

说明 CloudBase 确实去掉了 `/api` 前缀。

## 解决方案

### 方案 1: 修改 CloudBase HTTP 访问配置（推荐）

**目标**: 配置 CloudBase 不去除 `/api` 前缀

**步骤**:
1. 访问 CloudBase 控制台
2. 进入 HTTP 服务配置
3. 修改路由规则，保留 `/api` 前缀

**优点**:
- 保持代码一致性
- 不需要修改函数代码
- 符合 RESTful API 规范

**缺点**:
- 需要 CloudBase 控制台权限
- 配置可能比较复杂

### 方案 2: 修改函数路由代码

**目标**: 让函数同时支持 `/keyword` 和 `/api/keyword`

**步骤**:
修改 `functions/magic-rules-api/scf_index.py` 中的路由逻辑：

```python
# 修改前
if path == '/api/keyword':
    # 处理逻辑
    pass

# 修改后
if path == '/api/keyword' or path == '/keyword':
    # 处理逻辑
    pass
```

**优点**:
- 快速修复
- 不需要配置 CloudBase
- 兼容多种路径

**缺点**:
- 代码不够优雅
- 维护成本高
- 可能与其他 API 冲突

### 方案 3: 统一路径配置

**目标**: 在整个系统中统一使用 `/keyword` 而不是 `/api/keyword`

**步骤**:
1. 修改函数路由：`/keyword`
2. 修改客户端调用：`/keyword`
3. 更新所有文档

**优点**:
- 路径更简洁
- 代码统一
- 避免前缀问题

**缺点**:
- 破坏现有 API
- 需要大量修改
- 可能影响其他调用方

## 推荐方案

**短期解决方案**: 方案 2（修改函数路由代码）

**理由**:
1. 快速修复，立即可用
2. 不需要复杂的 CloudBase 配置
3. 不影响现有调用方

**长期解决方案**: 方案 1（配置 CloudBase）

**理由**:
1. 保持代码一致性
2. 符合 RESTful API 规范
3. 更好的可维护性

## 测试验证

### 修复后测试

1. **本地测试**:
   ```bash
   python3 tests/api_comparison.py
   ```

2. **云端测试**:
   ```bash
   curl "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/api/keyword?k=飞行"
   ```

3. **验证标准**:
   - 状态码: 200
   - 返回字段包含: `keyword`, `result`
   - `result` 包含: `keyword_name`, `description`, `full_text`, `examples`

## 影响范围

### 受影响的 API 端点

所有 `/api/*` 路径的 API 都可能受影响：

| 端点 | 状态 |
|------|------|
| `/api/search` | ✅ 正常（之前测试通过） |
| `/api/keyword` | ❌ 有问题 |
| `/api/card` | ✅ 正常（之前测试通过） |
| `/api/mtgch/search` | ❌ 有其他问题（依赖缺失） |
| `/api/mtgch/card` | ❌ 有其他问题（依赖缺失） |
| `/api/mtgch/random` | ❌ 有其他问题（依赖缺失） |
| `/api/mtgch/autocomplete` | ❌ 有其他问题（依赖缺失） |

### 说明

- `/api/search` 和 `/api/card` 之前测试通过，可能是因为测试时使用了不同的路径或配置
- `/api/keyword` 确认有路径不匹配问题
- `/api/mtgch/*` 有依赖缺失问题（`requests` 库未安装）

## 后续行动

### 立即行动（高优先级）

1. ✅ 完成问题分析
2. ⏳ 实施短期解决方案（方案 2）
3. ⏳ 验证修复效果
4. ⏳ 更新相关文档

### 中期行动（中优先级）

1. 实施长期解决方案（方案 1）
2. 解决 MTGCH API 依赖问题
3. 完善测试覆盖

### 长期行动（低优先级）

1. 统一 API 路径规范
2. 添加 API 版本控制
3. 完善 API 文档

## 相关文档

- [API测试报告](API测试报告.md)
- [本地API验证报告](本地API验证报告.md)
- [MTGCH API部署问题诊断](../deployment/docs/MTGCH API部署问题诊断.md)

---

**分析完成时间**: 2026-03-13
**分析工具**: tests/api_comparison.py
**分析人员**: AI Assistant
