# 集成测试

本目录包含集成测试，用于测试多个模块协同工作的功能。

## 测试文件

### test_first_stage.py

**功能**: 测试第一阶段完整功能

**测试内容**:
- 规则搜索功能
- 卡牌查询功能
- 关键词异能查询
- 问答模板

**运行方式**:
```bash
python tests/integration/test_first_stage.py
```

### test_card_service.py

**功能**: 测试卡牌服务完整功能

**测试内容**:
- 卡牌名称搜索（模糊匹配）
- 关键词异能搜索（216个关键词）
- 数据库统计功能
- 向量化数据准备

**运行方式**:
```bash
python tests/integration/test_card_service.py
```

### test_mtgch_api.py

**功能**: 测试MTGCH API客户端

**测试内容**:
- 卡牌搜索（中文/英文）
- 单张卡牌查询（UUID / set+number）
- 随机卡牌
- 自动补全

**运行方式**:
```bash
python tests/integration/test_mtgch_api.py
```

### test_rule_downloader.py

**功能**: 测试规则下载和解析功能

**测试内容**:
- 规则下载（TXT格式）
- 规则版本检查
- 规则内容解析
- 定时任务调度

**运行方式**:
```bash
python tests/integration/test_rule_downloader.py
```

## 运行所有集成测试

```bash
# 进入项目根目录
cd /Users/lianghaoming/cbworkplace

# 激活虚拟环境
source venv/bin/activate

# 运行所有集成测试
python tests/integration/test_first_stage.py
python tests/integration/test_card_service.py
python tests/integration/test_mtgch_api.py
python tests/integration/test_rule_downloader.py
```

## 测试依赖

- Python 3.10+
- 已安装项目依赖
- 数据库已初始化
- 网络连接正常（MTGCH API测试需要）

## 注意事项

1. MTGCH API测试需要网络连接
2. 规则下载测试会从官方API获取数据
3. 某些测试可能需要较长时间

---

**最后更新**: 2026-03-13
