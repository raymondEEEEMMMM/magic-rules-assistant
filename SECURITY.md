# 安全策略 / Security Policy

## 版本更新 / Version Updates

本项目会定期更新依赖包以修复已知安全漏洞。请确保使用最新版本。

We regularly update dependencies to fix known security vulnerabilities. Please ensure you are using the latest version.

## 报告安全漏洞 / Reporting Security Vulnerabilities

如果您发现了安全漏洞，请通过以下方式联系我们：

If you discover a security vulnerability, please contact us:

- **GitHub Issues**: https://github.com/raymondEEEEMMMM/magic-rules-assistant/issues

请在报告时包含以下信息：

Please include the following in your report:

1. 安全漏洞的详细描述 (Detailed description of the vulnerability)
2. 重现步骤 (Steps to reproduce)
3. 可能的利用方式 (Potential exploit scenarios)
4. 您的联系方式 (Your contact information)

## 安全最佳实践 / Security Best Practices

### 1. 环境变量管理 / Environment Variables

**重要**：敏感信息（如 API Key、数据库密码）必须通过环境变量配置，切勿硬编码在代码中。

**Important**: Sensitive information (such as API keys, database passwords) must be configured via environment variables. Never hardcode them in the code.

```bash
# 本地开发
cp .env.example .env.local
# 编辑 .env.local 填写实际配置

# 生产环境（CloudBase）
# 在 CloudBase 控制台的环境配置中设置环境变量
```

### 2. 数据库安全 / Database Security

- 使用强密码策略 (Use strong password policies)
- 遵循最小权限原则，数据库用户只授予必要的权限 (Follow the principle of least privilege)
- 云函数使用外网地址连接 MySQL，因为云函数无法访问内网 VPC (Cloud functions use public endpoints for MySQL)

### 3. API 安全 / API Security

当前版本的 API 端点**未实现**以下安全措施，生产环境部署时需要自行添加：

The current version of API endpoints **does not implement** the following security measures. You need to add them when deploying to production:

- [ ] 请求频率限制 (Request rate limiting)
- [ ] API 密钥认证 (API key authentication)
- [ ] CORS 配置 (CORS configuration)
- [ ] 请求大小限制 (Request size limits)
- [ ] SQL 注入防护（已使用参数化查询，但需持续关注）(SQL injection protection - parameterized queries are used)

### 4. 微信消息验证 / WeChat Message Verification

所有来自微信服务器的请求都会进行签名验证，请确保 `WECHAT_TOKEN` 配置正确。

All requests from WeChat servers are signature-verified. Ensure `WECHAT_TOKEN` is configured correctly.

## 依赖安全 / Dependency Security

定期检查依赖包的安全性：

Regularly check the security of dependencies:

```bash
# 使用 pip-audit 检查已知漏洞
pip install pip-audit
pip-audit

# 使用 npm audit（小程序前端）
cd miniprogram
npm audit
```

## 部署安全检查清单 / Deployment Security Checklist

- [ ] 所有敏感配置使用环境变量 (All sensitive configurations use environment variables)
- [ ] `.env.local` 文件已加入 `.gitignore`
- [ ] 数据库密码强度足够 (Database password is strong enough)
- [ ] 微信 Token 配置正确且保密 (WeChat token is configured correctly and kept secret)
- [ ] 考虑启用 API 频率限制 (Consider enabling API rate limiting)
- [ ] 定期更新依赖包 (Regularly update dependencies)
- [ ] 启用 CloudBase 日志监控 (Enable CloudBase log monitoring)
- [ ] 配置告警机制 (Configure alerting mechanisms)
