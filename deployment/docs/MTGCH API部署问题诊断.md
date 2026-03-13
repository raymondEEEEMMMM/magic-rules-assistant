# MTGCH API 部署问题诊断与解决方案

## 当前状态

### 环境信息
- 环境ID: `magic-rules-assistant-0a1904c329`
- 函数名称: `magic-rules-api`
- 函数类型: HTTP
- 运行时: Python 3.10
- 最后修改时间: 2026-03-13 13:59:05

### 访问地址
```
https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat
```

### 发现的问题

#### 1. 函数类型不匹配
**问题**: 当前函数是HTTP类型，但cloudbaserc.json配置使用`scf_index.main_handler`入口，这是Event类型函数的标准格式。

**HTTP类型函数特点**:
- 使用`scf_bootstrap`启动脚本
- 需要监听9000端口
- 运行一个完整的HTTP服务器
- 不能使用`main_handler`

**Event类型函数特点**:
- 使用`main_handler`函数入口
- 每次请求调用一次
- 不需要运行HTTP服务器

#### 2. 依赖缺失
**问题**: `/functions/magic-rules-api/requirements.txt` 不存在，导致requests库没有安装。

**已修复**: 已创建requirements.txt，但需要重新部署才能生效。

#### 3. 路由未生效
**测试结果**:
```bash
GET /wechat/api/mtgch/search
# 返回: {"message": "万智牌规则问答服务运行中", ...}
# 预期: MTGCH API的搜索结果
```

**原因**: 代码走到了默认的fallback响应，说明：
- MTGCH API路由代码没有执行到
- 可能是导入错误（requests未安装）
- 或者是路由配置问题

## 解决方案

### 方案A: 切换为Event类型函数（推荐）

**优点**:
- 更简单，更容易调试
- 不需要运行HTTP服务器
- 依赖管理更清晰
- 与cloudbaserc.json配置一致

**步骤**:

1. 删除当前HTTP类型函数
2. 重新创建Event类型函数
3. 使用根目录的`scf_index.py`作为入口

**配置**:
```json
{
  "functions": [
    {
      "name": "magic-rules-api",
      "type": "Event",
      "runtime": "Python3.10",
      "handler": "scf_index.main_handler"
    }
  ]
}
```

**文件结构**:
```
/Users/lianghaoming/cbworkplace/
├── scf_index.py           # Event类型入口（已更新MTGCH路由）
├── requirements.txt       # 依赖
└── backend/
    └── services/
        └── mtgch_api.py   # MTGCH API客户端
```

### 方案B: 修复HTTP类型函数

**优点**:
- 不需要改变函数类型
- HTTP访问配置已存在

**步骤**:

1. 确保依赖安装
   - 在`functions/magic-rules-api/`下创建`requirements.txt`
   - 使用CloudBase CLI手动安装依赖

2. 检查路由逻辑
   - 确认路径解析正确
   - 检查异常处理

3. 重新部署

**CloudBase CLI命令**:
```bash
# 部署HTTP函数
tcb fn deploy magic-rules-api -e magic-rules-assistant-0a1904c329 --httpFn --yes

# 或使用本地命令
cd /Users/lianghaoming/cbworkplace
tcb functions:deploy magic-rules-api
```

### 方案C: 使用CloudBase CLI重新部署

如果MCP工具超时或失败，可以直接使用CloudBase CLI：

```bash
# 1. 登录CloudBase
tcb login

# 2. 部署函数
tcb fn deploy magic-rules-api -e magic-rules-assistant-0a1904c329 --httpFn --yes

# 3. 查看函数状态
tcb fn list -e magic-rules-assistant-0a1904c329

# 4. 查看日志
tcb logs get -e magic-rules-assistant-0a1904c329 --fn magic-rules-api
```

## 推荐操作步骤

### 短期（快速解决）

1. 使用CloudBase CLI手动部署
2. 查看函数日志确认依赖是否安装
3. 测试API端点

### 长期（优化架构）

1. 考虑切换为Event类型函数
2. 统一使用一个scf_index.py文件
3. 简化依赖管理

## 测试验证

部署完成后，测试以下端点：

```bash
# 中文牌查询
curl "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/search?q=闪电风暴&priority_chinese=true"

# 英文牌查询
curl "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/search?q=Lightning Storm&priority_chinese=false"

# 随机卡牌
curl "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/random"
```

## 已完成的准备工作

✅ MTGCH API客户端已创建
✅ MTGCH路由已添加到scf_index.py（两个版本）
✅ requirements.txt已创建（HTTP版本）
✅ 文档已更新

## 下一步

需要手动执行以下任一操作：

1. **使用CloudBase CLI重新部署**（推荐）
2. **在CloudBase控制台手动更新代码**
3. **切换为Event类型函数**（需要删除重建）

---

**更新时间**: 2026-03-13
**状态**: 等待部署验证
