# CloudBase 部署指南

## ⚠️ 部署关键要点

### 1. 云函数类型选择
- **Event 类型**：不是 HTTP 类型，通过 HTTP 访问路径访问
- **HTTP 类型**：可以直接用 URL 访问，但配置更复杂

### 2. Event 函数特殊配置
- **入口文件**：`scf_index.py`（不是 `index.py`）
- **Handler**：`scf_index.main_handler`
- **依赖上传**：Event 函数不会自动安装依赖，需要：
  1. 创建 `vendor` 目录
  2. 复制依赖到 vendor：`cp -r venv/lib/python3.10/site-packages/* functions/mtgAsk/vendor/`
  3. 上传 vendor 目录

### 3. scf_bootstrap 配置
```bash
#!/bin/bash
export PYTHONPATH=/var/user/vendor:$PYTHONPATH
exec python3 -u scf_index.py
```

### 4. MySQL 数据库
- **使用外网主机名**：如 `sh-cynosdbmysql-grp-xxx.sql.tencentcdb.com`
- **端口**：外网端口（如 27987），不是 3306

### 5. HTTP 访问路径
- 微信路径前缀：`/wechat/api/...`
- 示例：`/wechat/api/mtgch/search`

---

## 准备工作

### 1. 安装 CloudBase CLI

```bash
npm install -g @cloudbase/cli
```

### 2. 登录腾讯云

```bash
cloudbase login
```

### 3. 创建 CloudBase 环境

访问 [腾讯云 CloudBase 控制台](https://console.cloud.tencent.com/tcb) 创建新环境

## 部署步骤

### 方式一：使用云容器服务（推荐）

1. **修改配置文件**

编辑 `cloudbaserc.json`，填入你的环境 ID：

```json
{
  "envId": "your-env-id"
}
```

2. **部署**

```bash
cloudbase deploy
```

3. **获取访问地址**

部署成功后，CloudBase 会提供一个访问地址，类似：
```
https://your-env-id.service.tcloudbase.com
```

### 方式二：使用云函数（轻量级）

1. **创建云函数配置**

修改 `cloudbaserc.json`：

```json
{
  "envId": "your-env-id",
  "version": "2.0",
  "framework": {
    "name": "magic-rules-assistant",
    "plugins": {
      "function": {
        "use": "@cloudbase/framework-plugin-function",
        "inputs": {
          "functions": {
            "wechat-api": {
              "handler": "main.main",
              "runtime": "Python3.10",
              "timeout": 60,
              "memorySize": 256,
              "envVariables": {
                "ENVIRONMENT": "production"
              }
            }
          }
        }
      }
    }
  }
}
```

2. **部署**

```bash
cloudbase functions:deploy
```

## 微信公众号配置

### 1. 获取服务器信息

部署后获取：
- **服务器地址（URL）**：`https://your-domain.com/wechat`
- **Token**：在 `backend/.env` 中设置的 `WECHAT_TOKEN`

### 2. 微信公众号后台配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 进入「开发」->「基本配置」
3. 修改「服务器配置」：
   - URL: `https://your-domain.com/wechat`
   - Token: 你设置的 Token
   - EncodingAESKey: 随机生成或自定义
   - 消息加解密方式：选择「明文模式」

### 3. 启用服务器配置

点击「提交」验证服务器地址，验证通过后点击「启用」

## 测试验证

### 1. 测试服务状态

```bash
curl https://your-domain.com/
```

应返回：
```json
{"message": "万智牌规则问答服务运行中", "status": "ok"}
```

### 2. 测试微信验证

访问：
```
https://your-domain.com/wechat?signature=xxx&timestamp=xxx&nonce=xxx&echostr=hello
```

### 3. 在微信公众号测试

关注你的公众号，发送消息测试：
- "飞行" - 查询关键词异能
- "黑莲花" - 查询卡牌规则
- "飞行规则" - 搜索规则

## 常见问题

### 1. 部署失败

检查 `cloudbaserc.json` 配置是否正确，确保环境 ID 正确

### 2. 微信验证失败

- 检查 URL 是否可访问
- 检查 Token 是否与 `backend/.env` 中一致
- 检查服务器是否返回 echostr

### 3. 云函数超时

增加函数超时时间：
```json
"timeout": 120
```

### 4. 内存不足

增加函数内存：
```json
"memorySize": 512
```

## 环境变量配置

在 CloudBase 控制台或 `cloudbaserc.json` 中配置：

```json
"envVariables": {
  "ENVIRONMENT": "production",
  "API_HOST": "0.0.0.0",
  "API_PORT": "80",
  "WECHAT_TOKEN": "your-wechat-token",
  "OPENAI_API_KEY": "your-openai-key"
}
```

## 成本估算

CloudBase 云函数：
- 免费额度：10万次调用/月
- 超出后：约 ¥0.0000167/次

云容器服务：
- 免费额度：5元/月（CPU 0.5核，内存 0.5GB）
- 超出后：按量计费

## 监控和日志

访问 CloudBase 控制台：
- **云函数日志**：查看函数执行日志
- **云容器日志**：查看容器日志
- **监控**：查看调用次数、错误率等

## 更新部署

代码修改后重新部署：

```bash
cloudbase deploy
```

或只部署特定函数：

```bash
cloudbase functions:deploy wechat-api
```
