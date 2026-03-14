# 云函数测试

本目录包含CloudBase云函数相关测试。

## 测试文件

### test_cloud_mtgch.py

**版本**: v1

**功能**: CloudBase云函数MTGCH API测试（初版）

**测试内容**:
- HTTP访问路径测试
- MTGCH API端点测试
- 参数验证

**状态**: ✅ 完成

### test_cloud_mtgch_correct.py

**版本**: 修正版

**功能**: CloudBase云函数MTGCH API测试（修正版）

**改进点**:
- 修复了路径解析问题
- 改进了错误处理
- 添加了更多测试用例

**状态**: ✅ 完成

### test_cloud_mtgch_v2.py

**版本**: v2

**功能**: CloudBase云函数MTGCH API测试（v2版）

**改进点**:
- 简化了测试流程
- 优化了响应处理
- 改进了日志输出

**状态**: ✅ 完成

## 运行测试

### 前置条件

1. 已安装CloudBase CLI
2. 已登录CloudBase账号
3. 云函数已部署
4. HTTP访问路径已配置

### 运行方式

```bash
# 进入项目根目录
cd /Users/lianghaoming/cbworkplace

# 激活虚拟环境
source venv/bin/activate

# 运行云函数测试
python tests/cloud/test_cloud_mtgch_correct.py
```

## 当前状态

### 已部署的云函数

- **函数名称**: `magic-rules-api`
- **运行环境**: Python 3.10
- **内存**: 512MB
- **超时**: 60s
- **状态**: Deployment completed

### HTTP访问

- **访问域名**: `https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com`
- **API端点**:
  - `/api/mtgch/search?q=卡牌名&page_size=5`
  - `/api/mtgch/card?id=UUID`
  - `/api/mtgch/random`
  - `/api/mtgch/autocomplete?q=关键词&size=10`

### 已知问题

1. **路由匹配问题**: 所有请求返回默认响应
2. **依赖安装问题**: requests库未自动安装

### 解决方案

1. 在CloudBase控制台启用"自动安装依赖"
2. 检查HTTP访问路径配置
3. 重新部署函数确保代码更新

## 测试结果

### 最新测试结果

```python
✅ 函数健康检查: 通过
⚠️ 随机卡牌API: 返回默认响应（路由匹配问题）
⚠️ 卡牌搜索API: 返回默认响应（路由匹配问题）
⚠️ 自动补全API: 返回默认响应（路由匹配问题）
```

## 云函数信息

### 部署详情

```
Environment ID: magic-rules-assistant-0a1904c329
Function Name: magic-rules-api
Function ID: lam-piraj8gd
Runtime: Python3.10
Code Size: 386,964,088 bytes (~369MB)
Memory: 512MB
Timeout: 60s
Status: Deployment completed
```

### 环境变量

```
ENVIRONMENT=production
WECHAT_TOKEN=wx_mtg_rules_2024
```

### 控制台链接

https://tcb.cloud.tencent.com/dev?envId=magic-rules-assistant-0a1904c329#/scf

## 相关文档

- [CloudBase部署指南](../../docs/CloudBase部署指南.md)
- [MTGCH API最终部署报告](../../docs/MTGCH%20API最终部署报告.md)
- [MTGCH部署最终总结](../../docs/MTGCH部署最终总结.md)

---

**最后更新**: 2026-03-13
**云函数状态**: 部分可用，待解决问题
