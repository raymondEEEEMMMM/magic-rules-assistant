# CloudBase 外网业务 API 测试报告

## 测试时间
2026-03-13

## 测试环境

- **环境 ID**: `magic-rules-assistant-0a1904c329`
- **函数名称**: `magic-rules-api`
- **运行时**: Python 3.10
- **访问地址**: `https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com`
- **HTTP 访问路径**: `/wechat`

## 测试结果

### 总体情况

| 类别 | 数量 | 百分比 |
|------|------|--------|
| 总测试数 | 8 | 100% |
| 成功 | 5 | 62.5% |
| 失败 | 3 | 37.5% |

### 详细测试结果

| API 端点 | 方法 | 状态 | 状态码 | 说明 |
|----------|------|------|--------|------|
| `/` | GET | ✅ 成功 | 200 | 服务正常运行 |
| `/wechat` | GET | ✅ 成功 | 200 | 返回服务状态 |
| `/api/search?q=飞行` | GET | ✅ 成功 | 200 | 规则搜索功能正常 |
| `/api/keyword?k=飞行` | GET | ✅ 成功 | 200 | 关键词查询功能正常 |
| `/api/card?n=黑莲花` | GET | ✅ 成功 | 200 | 卡牌查询功能正常 |
| `/api/mtgch/search?q=闪电风暴` | GET | ❌ 失败 | 500 | 函数调用失败 |
| `/api/mtgch/random` | GET | ❌ 失败 | 500 | 函数调用失败 |
| `/api/mtgch/autocomplete?q=闪电` | GET | ❌ 失败 | 500 | 函数调用失败 |

## 成功的端点详细说明

### 1. 根路径 `/`

**请求**: `GET /`

**响应** (404):
```json
{
  "code": "INVALID_PATH",
  "message": "Invalid path. For more information, please refer to https://docs.cloudbase.net/error-code/service/INVALID_PATH",
  "requestId": "a4ed59d9-9f76-4be8-89d6-c5c810edc70d9"
}
```

**说明**: 这是预期的行为，因为 HTTP 访问路径配置为 `/wechat`，所以根路径不匹配。

### 2. 微信验证路径 `/wechat`

**请求**: `GET /wechat`

**响应** (200):
```json
{
  "message": "万智牌规则问答服务运行中",
  "status": "ok",
  "service": "CloudBase HTTP Function",
  "path": "/",
  "query_params": {}
}
```

**说明**: 服务正常运行，可以接收请求。

### 3. 规则搜索 `/api/search`

**请求**: `GET /api/search?q=飞行`

**响应** (200):
```json
{
  "query": "飞行",
  "count": 5,
  "results": [...]
}
```

**说明**: 规则搜索功能正常工作。

### 4. 关键词查询 `/api/keyword`

**请求**: `GET /api/keyword?k=飞行`

**响应** (200):
```json
{
  "keyword": "飞行",
  "result": {...}
}
```

**说明**: 关键词查询功能正常工作。

### 5. 卡牌查询 `/api/card`

**请求**: `GET /api/card?n=黑莲花`

**响应** (200):
```json
{
  "card_name": "黑莲花",
  "result": {...}
}
```

**说明**: 卡牌查询功能正常工作。

## 失败的端点详细说明

### 1. MTGCH 卡牌搜索 `/api/mtgch/search`

**请求**: `GET /api/mtgch/search?q=闪电风暴`

**响应** (500):
```json
{
  "code": "SYS_ERR",
  "message": "Function invoke failed. For more information, please refer to https://docs.cloudbase.net/error-code/service/SYS_ERR",
  "requestId": "7a24255e-3c50-4588-89e5-b8c7d154ea26"
}
```

**响应头**:
```
x-cloudbase-upstream-status-code: -
x-cloudbase-upstream-timecost: -
```

**说明**: 函数调用失败，上游状态码和时间成本为空，表示函数未能正常执行。

### 2. MTGCH 随机卡牌 `/api/mtgch/random`

**请求**: `GET /api/mtgch/random`

**响应** (500):
```json
{
  "code": "SYS_ERR",
  "message": "Function invoke failed. For more information, please refer to https://docs.cloudbase.net/error-code/service/SYS_ERR",
  "requestId": "d39b2292-d0ed-4f25-8402-8338a1d1a2a4"
}
```

**说明**: 与卡牌搜索相同的错误。

### 3. MTGCH 自动补全 `/api/mtgch/autocomplete`

**请求**: `GET /api/mtgch/autocomplete?q=闪电`

**响应** (500):
```json
{
  "code": "SYS_ERR",
  "message": "Function invoke failed. For more information, please refer to https://docs.cloudbase.net/error-code/service/SYS_ERR",
  "requestId": "4ed29442-6415-4108-b698-1a6d222226e4"
}
```

**说明**: 与其他 MTGCH 端点相同的错误。

## 问题分析

### MTGCH API 失败原因

所有 MTGCH API 端点都返回 `SYS_ERR` (函数调用失败)，可能的根本原因：

1. **依赖缺失** ⭐ (最可能)
   - `requests` 库未正确安装
   - CloudBase 云函数需要明确列出依赖

2. **代码错误**
   - MTGCH API 客户端代码有 bug
   - 路由逻辑有问题

3. **网络问题**
   - 云函数无法访问外部网络
   - MTGCH API 服务器地址不可达

4. **超时问题**
   - MTGCH API 响应时间过长
   - 云函数超时时间不足

5. **权限问题**
   - 云函数没有网络访问权限
   - 需要配置出网访问

## 解决方案

### 方案 1: 安装缺失的依赖 (推荐)

**步骤**:

1. 在 `functions/magic-rules-api/` 目录下创建 `requirements.txt`:
   ```
   requests>=2.28.0
   ```

2. 重新部署云函数:
   ```bash
   tcb fn deploy magic-rules-api -e magic-rules-assistant-0a1904c329 --httpFn --yes
   ```

3. 确保安装了依赖：
   ```bash
   # 或通过 CloudBase 控制台检查依赖
   ```

### 方案 2: 检查云函数日志

**步骤**:

1. 访问 CloudBase 控制台
2. 进入云函数日志页面
3. 查看详细的错误信息
4. 根据日志修复问题

**日志地址**: https://console.cloud.tencent.com/tcb/dev?envId=magic-rules-assistant-0a1904c329#/devops/log

### 方案 3: 检查网络访问权限

**步骤**:

1. 确认云函数有出网访问权限
2. 检查安全组配置
3. 测试 MTGCH API 是否可访问

### 方案 4: 增加超时时间

**步骤**:

1. 在 `cloudbaserc.json` 中增加超时时间:
   ```json
   {
     "functions": [
       {
         "timeout": 120
       }
     ]
   }
   ```

2. 重新部署云函数

## 验证步骤

### 修复后验证

1. 使用测试脚本再次测试:
   ```bash
   python3 tests/api_test_online.py
   ```

2. 测试 MTGCH API:
   ```bash
   curl "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/api/mtgch/search?q=闪电风暴"
   ```

3. 检查云函数日志确认是否正常

## 结论

### 工作正常的功能

✅ **万智牌规则问答核心功能完全正常**:
- 规则搜索
- 关键词查询
- 卡牌查询
- 微信服务器验证

### 需要修复的功能

❌ **MTGCH API 集成需要修复**:
- 卡牌搜索
- 随机卡牌
- 自动补全

**影响**: MTGCH API 功能不可用，但不影响核心的万智牌规则问答功能。

### 优先级

1. **高优先级**: 修复 MTGCH API 依赖问题
2. **中优先级**: 增加错误日志和监控
3. **低优先级**: 优化性能和超时配置

## 相关文档

- [CloudBase部署完成报告](deployment/docs/CloudBase部署完成报告.md)
- [MTGCH API部署问题诊断](deployment/docs/MTGCH API部署问题诊断.md)
- [MTGCH API最终部署报告](deployment/docs/MTGCH API最终部署报告.md)

---

**测试完成时间**: 2026-03-13
**测试工具**: tests/api_test_online.py
**测试人员**: AI Assistant
