# 微信公众号集成文档

## 概述

本文档介绍如何将万智牌规则问答服务与微信公众号集成。

## 目录结构

```
wechat_integration/
├── config/               # 配置文件
│   ├── env.example      # 环境变量模板
│   └── menu.json        # 菜单配置
├── scripts/             # 脚本工具
│   ├── set_menu.py      # 菜单设置脚本
│   └── verify_wechat.py # 配置验证脚本
└── docs/                # 文档
    └── README.md        # 本文档
```

## 快速开始

### 1. 配置环境变量

```bash
# 复制配置模板
cp config/env.example config/.env

# 编辑配置，填入实际值
vim config/.env
```

必需配置：
- `WECHAT_APP_ID` - 公众号 AppID
- `WECHAT_APP_SECRET` - 公众号 AppSecret

### 2. 验证配置

```bash
cd wechat_integration/scripts
python3 verify_wechat.py
```

### 3. 设置自定义菜单

```bash
# 方式1：环境变量
export WECHAT_APP_ID="your_app_id"
export WECHAT_APP_SECRET="your_app_secret"
python3 set_menu.py

# 方式2：命令行参数
python3 set_menu.py -i your_app_id -s your_app_secret
```

## 公众号配置获取

### 获取 AppID 和 AppSecret

1. 登录微信公众号后台：https://mp.weixin.qq.com/
2. **AppID**: 开发 → 开发设置 → 公众号设置 → 账号详情
3. **AppSecret**: 开发 → 开发设置 → 公众号开发信息 → 查看/重置

### 添加 IP 白名单

1. 开发 → 开发设置 → 公众号开发信息
2. IP白名单 → 添加 IP
3. 需添加的 IP：
   - 公网 IP（运行脚本的服务器）
   - CloudBase 云函数出口 IP（可选）

### 配置服务器 URL

1. 开发 → 基本配置
2. 服务器配置 → 修改配置
3. 填写：
   - URL: `https://你的环境Id.ap-shanghai.app.tcloudbase.com/wechat`
   - Token: `wx_mtg_rules_2024`（或自定义）
   - 消息加解密方式: 纯明文模式

## 菜单配置说明

### 菜单 Key 对应功能

| Key | 功能 | 返回内容 |
|-----|------|----------|
| `keyword_search` | 关键词查询说明 | 关键词查询使用帮助 |
| `rule_search` | 规则搜索说明 | 规则搜索使用帮助 |
| `card_search` | 卡牌查询说明 | 卡牌查询使用帮助 |
| `feature_intro` | 功能介绍 | 服务功能列表 |
| `about` | 关于服务 | 服务介绍 |

### 菜单 JSON 结构

```json
{
  "button": [
    {
      "name": "规则查询",
      "sub_button": [
        {"type": "click", "name": "关键词查询", "key": "keyword_search"},
        {"type": "click", "name": "规则搜索", "key": "rule_search"},
        {"type": "click", "name": "卡牌查询", "key": "card_search"}
      ]
    },
    {
      "name": "使用帮助",
      "sub_button": [
        {"type": "click", "name": "功能介绍", "key": "feature_intro"},
        {"type": "click", "name": "关于服务", "key": "about"}
      ]
    }
  ]
}
```

## 公众号类型与权限

| 类型 | 自定义菜单 API | 说明 |
|------|---------------|------|
| 订阅号(未认证) | ❌ 无 | 需手动配置 |
| 订阅号(认证) | ✅ 有 | 需认证 |
| 服务号 | ✅ 有 | 完整权限 |

**注意**: 未认证的订阅号无法通过 API 创建菜单，需要在微信后台手动配置。

## 云函数配置

### 环境变量

在 `cloudbaserc.json` 中配置：

```json
{
  "functions": [
    {
      "name": "magic-rules-api",
      "envVariables": {
        "WECHAT_TOKEN": "wx_mtg_rules_2024"
      },
      "http": {
        "path": "/"
      }
    }
  ]
}
```

### HTTP 访问

确保云函数已配置 HTTP 访问路径为 `/`，以便接收微信消息。

## 消息处理

### 接收的消息类型

- **文本消息**: 用户发送的文本内容
- **事件消息**: 用户点击菜单、关注等

### 回复格式

```xml
<xml>
  <ToUserName><![CDATA[用户OpenID]]></ToUserName>
  <FromUserName><![CDATA[公众号ID]]></FromUserName>
  <CreateTime>1234567890</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[回复内容]]></Content>
</xml>
```

## 常见问题

### 1. 获取 access_token 失败

**错误**: `invalid ip, not in whitelist`

**解决**: 在微信后台添加服务器 IP 到白名单

### 2. 菜单创建失败

**错误**: `api unauthorized (48001)`

**原因**: 订阅号未认证，没有菜单 API 权限

**解决**: 手动在微信后台配置菜单

### 3. 消息验证失败

**检查**:
1. Token 是否正确
2. 签名算法是否正确
3. 服务器 URL 是否可访问

## 相关文件

- `cloudbaserc.json` - CloudBase 项目配置
- `functions/magic-rules-api/scf_index.py` - 云函数入口
- `backend/config.py` - 后端配置
