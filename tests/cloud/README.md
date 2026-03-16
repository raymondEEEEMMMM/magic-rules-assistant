# 云函数测试

本目录包含 CloudBase 云函数相关测试。

## ⚠️ 关键要点

### 云函数类型
- **Event 类型云函数**：不是 HTTP 类型，需要通过 HTTP 访问路径访问
- **scf_index.py**：Event 函数的入口文件，handler 设为 `scf_index.main_handler`

### 依赖管理
- **vendor 目录**：Event 函数不会自动安装依赖，需要将依赖打包上传
- **PYTHONPATH**：在 `scf_bootstrap` 中设置 `export PYTHONPATH=/var/user/vendor:$PYTHONPATH`

### 数据库连接
- **云端 MySQL**：使用外网主机名（如 `sh-cynosdbmysql-grp-xxx.sql.tencentcdb.com`）
- **端口**：外网端口（如 27987），不是内网端口 3306

### API 访问
- **正确路径**：`/wechat/api/mtgch/search`（不是 `/api/mtgch/search`）
- **环境变量**：`WECHAT_TOKEN` 用于微信验证

---

## 测试文件

### test_cloud_mtgch.py

**版本**: v1

**功能**: CloudBase 云函数 MTGCH API 测试（初版）

**访问 URL**: `https://magic-rules-assistant-0a1904c329.service.tcloudbaseapp.com/magic-rules-api`

**测试内容**:
- HTTP 访问路径测试
- MTGCH API 端点测试
- 参数验证

**状态**: 默认跳过（需要外部网络）

### test_cloud_mtgch_correct.py

**版本**: 修正版

**功能**: CloudBase 云函数 MTGCH API 测试（修正版）

**访问 URL**: `https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com`

**测试内容**:
- 根路径测试
- 中文卡牌搜索
- 英文卡牌搜索
- 随机卡牌
- 自动补全

**状态**: 默认跳过（需要外部网络）

### test_cloud_mtgch_v2.py

**版本**: v2

**功能**: CloudBase 云函数 MTGCH API 测试（微信路径）

**访问 URL**: `https://magic-rules-assistant-0a1904c329.ap-shanghai.tcloudbaseapp.com/wechat`

**测试内容**:
- 微信路径访问
- 中文搜索
- 随机卡牌

**状态**: 默认跳过（需要外部网络）

## 运行测试

### 前置条件

1. 已安装 CloudBase CLI
2. 已登录 CloudBase 账号
3. 云函数已部署
4. HTTP 访问路径已配置
5. 网络连接正常

### 运行方式

```bash
# 运行云函数测试（会被跳过）
pytest tests/cloud/ -v

# 如果需要实际测试，移除 skip 标记
pytest tests/cloud/ -v -m cloud
```

## pytest 标记

云函数测试使用以下标记：

```python
@pytest.mark.cloud
@pytest.mark.api
@pytest.mark.skip(reason="需要外部网络连接")
def test_chinese_search(self):
    ...
```

## API 端点

### 正确访问路径

| 端点 | URL |
|------|-----|
| 搜索 | `/wechat/api/mtgch/search?q=闪电风暴` |
| 随机 | `/wechat/api/mtgch/random` |
| 自动补全 | `/wechat/api/mtgch/autocomplete?q=闪电` |

### 云函数信息

- **环境 ID**: magic-rules-assistant-0a1904c329
- **函数名称**: mtgAsk
- **函数类型**: Event（事件型）
- **入口文件**: scf_index.py
- **Handler**: scf_index.main_handler
- **运行环境**: Python 3.10
- **内存**: 512MB
- **超时**: 60s
- **依赖方式**: vendor 目录

### 测试验证命令

```bash
# 测试关键词查询（英文）
curl 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/keyword?k=Flying'

# 测试卡牌搜索（中文）
curl 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/search?q=闪电风暴'
```

---

**最后更新**: 2026-03-16
**测试框架**: pytest
