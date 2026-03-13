# MTGJSON 卡牌数据需求分析

## 📋 可用文件列表

根据 MTGJSON 官网，以下是我们可能需要的文件：

### 核心卡牌数据

#### 1. **AllPrintings.json** ⭐⭐⭐⭐⭐ (强烈推荐)
- **描述**: 包含所有系列的完整卡牌数据，使用 Card(Set) 数据模型
- **格式**: JSON (支持 bz2, gz, xz, zip 压缩)
- **大小**: 约 200-500MB (未压缩)
- **内容**: 所有卡牌的所有印次和变体
- **推荐压缩格式**: `AllPrintings.json.gz` 或 `AllPrintings.json.bz2`

#### 2. **AtomicCards.json** ⭐⭐⭐⭐ (推荐)
- **描述**: 按卡牌名称组织的所有卡牌数据（去重）
- **格式**: JSON (支持多种压缩)
- **大小**: 约 50-100MB (未压缩)
- **内容**: 每张卡牌的完整信息（不区分不同印次）
- **适用场景**: 快速查询卡牌信息，不关心具体印次

#### 3. **AllIdentifiers.json** ⭐⭐⭐
- **描述**: 所有卡牌的标识符（按UUID组织）
- **格式**: JSON (支持多种压缩)
- **大小**: 约 10-20MB
- **内容**: 卡牌的各类标识符（Scryfall ID、TCGplayer ID等）
- **适用场景**: 快速查找卡牌标识符

### 辅助数据

#### 4. **Keywords.json** ⭐⭐⭐⭐ (推荐)
- **描述**: 所有卡牌关键词列表
- **格式**: JSON (支持多种压缩)
- **大小**: 约 10-50KB
- **内容**: 关键词异能的定义和分类
- **适用场景**: 与规则系统关联

#### 5. **CardTypes.json** ⭐⭐
- **描述**: 所有卡牌类型
- **格式**: JSON (支持多种压缩)
- **大小**: 约 10-20KB
- **内容**: 卡牌类型的完整分类

#### 6. **SetList.json** ⭐⭐⭐
- **描述**: 所有系列的元数据列表
- **格式**: JSON (支持多种压缩)
- **大小**: 约 20-50KB
- **内容**: 系列名称、代码、发布日期等

### 数据库格式

#### 7. **AllPrintings.sqlite** ⭐⭐⭐⭐⭐ (强烈推荐)
- **描述**: SQLite 数据库格式的完整卡牌数据
- **格式**: SQLite (支持多种压缩)
- **大小**: 约 100-300MB
- **内容**: 与 AllPrintings.json 相同的数据，但已结构化
- **优势**: 无需解析，直接查询，适合生产环境
- **推荐压缩格式**: `AllPrintings.sqlite.gz`

### 竞赛格式数据（可选）

#### 8. **Standard.json / StandardAtomic.json**
- **描述**: Standard 竞赛格式合法的卡牌
- **适用场景**: 专注 Standard 格式的查询

#### 9. **Modern.json / ModernAtomic.json**
- **描述**: Modern 竞赛格式合法的卡牌
- **适用场景**: 专注 Modern 格式的查询

#### 10. **Legacy.json / LegacyAtomic.json**
- **描述**: Legacy 竞赛格式合法的卡牌
- **适用场景**: 专注 Legacy 格式的查询

## 🎯 推荐方案

### 方案 A：完整数据方案（推荐）⭐⭐⭐⭐⭐

适合需要完整卡牌数据和规则的系统：

| 文件 | 用途 | 推荐格式 |
|------|------|---------|
| AllPrintings.json.gz | 完整卡牌数据（开发/测试） | gzip 压缩 |
| AllPrintings.sqlite.gz | 完整卡牌数据（生产） | gzip 压缩 |
| Keywords.json | 关键词异能 | JSON |
| SetList.json | 系列列表 | JSON |

**优点**:
- ✅ 数据完整，包含所有卡牌
- ✅ SQLite 格式直接可用，无需复杂解析
- ✅ 支持向量化搜索
- ✅ 适合生产环境部署

**缺点**:
- ❌ 文件较大（约 300-500MB）
- ❌ 下载和更新耗时较长

### 方案 B：轻量级方案

适合快速原型开发和测试：

| 文件 | 用途 | 推荐格式 |
|------|------|---------|
| AtomicCards.json.gz | 基础卡牌数据 | gzip 压缩 |
| Keywords.json | 关键词异能 | JSON |
| AllIdentifiers.json | 卡牌标识符 | JSON |

**优点**:
- ✅ 文件较小（约 100MB）
- ✅ 下载快速
- ✅ 适合开发测试

**缺点**:
- ❌ 数据不完整（缺少部分印次）
- ❌ 需要手动解析 JSON

## 📊 Card(Set) 数据模型分析

### 关键字段（规则查询相关）

| 字段 | 类型 | 说明 | 必需性 |
|------|------|------|--------|
| `name` | string | 卡牌名称 | ⭐⭐⭐⭐⭐ |
| `text` | string | 规则文本 | ⭐⭐⭐⭐⭐ |
| `type` | string | 卡牌类型 | ⭐⭐⭐⭐ |
| `types` | string[] | 类型列表 | ⭐⭐⭐⭐ |
| `subtypes` | string[] | 子类型列表 | ⭐⭐⭐ |
| `supertypes` | string[] | 超类型列表 | ⭐⭐⭐ |
| `manaCost` | string | 法术力费用 | ⭐⭐⭐⭐ |
| `manaValue` | number | 法术力值 | ⭐⭐⭐ |
| `colors` | string[] | 颜色 | ⭐⭐⭐ |
| `colorIdentity` | string[] | 颜色身份 | ⭐⭐⭐ |
| `keywords` | string[] | 关键词异能 | ⭐⭐⭐⭐⭐ |
| `power` | string | 攻击力 | ⭐⭐ |
| `toughness` | string | 防御力 | ⭐⭐ |
| `legalities` | Legalities | 合法性信息 | ⭐⭐⭐ |
| `rulings` | Rulings[] | 官方裁定 | ⭐⭐⭐⭐ |
| `uuid` | string | 唯一标识符 | ⭐⭐⭐⭐⭐ |
| `setCode` | string | 系列代码 | ⭐⭐⭐ |
| `rarity` | string | 稀有度 | ⭐⭐ |

### 示例数据结构

```json
{
  "name": "Black Lotus",
  "manaCost": "{0}",
  "manaValue": 0,
  "colors": [],
  "colorIdentity": [],
  "type": "Artifact",
  "types": ["Artifact"],
  "text": "T, Sacrifice Black Lotus: Add three mana of any one color.",
  "keywords": [],
  "power": "",
  "toughness": "",
  "rarity": "rare",
  "setCode": "LEA",
  "uuid": "d3355b16-6f1a-4f1f-b8e7-df852d416a28",
  "legalities": {
    "standard": "not_legal",
    "modern": "not_legal",
    "legacy": "restricted",
    "vintage": "restricted"
  },
  "rulings": [
    {
      "date": "2004-10-04",
      "text": "Black Lotus is not legal in tournaments."
    }
  ]
}
```

## 🔧 数据下载和解析建议

### 下载格式选择

| 场景 | 推荐格式 | 原因 |
|------|---------|------|
| 开发/测试 | `AllPrintings.json.gz` | 易于解析，压缩率高 |
| 生产环境 | `AllPrintings.sqlite.gz` | 直接查询，无需解析 |
| 向量化 | `AllPrintings.json` | 纯文本，易于处理 |
| 紧急更新 | `AllPrintings.json.xz` | 压缩率最高 |

### 下载地址

MTGJSON 文件服务器地址：
```
https://mtgjson.com/api/v5/AllPrintings.json.gz
https://mtgjson.com/api/v5/AllPrintings.sqlite.gz
https://mtgjson.com/api/v5/Keywords.json
https://mtgjson.com/api/v5/SetList.json
```

### 版本检查

建议先下载 `Meta.json` 检查最新版本：
```json
{
  "date": "2026-03-12",
  "version": "5.2.2"
}
```

## 📝 集成建议

### 1. 数据存储方案

**方案 A: 直接使用 SQLite（推荐）**
```python
# 直接查询 AllPrintings.sqlite
import sqlite3
conn = sqlite3.connect('data/cards/AllPrintings.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT * FROM cards WHERE name LIKE ?", ('Black Lotus',))
```

**方案 B: 解析 JSON 后导入自定义数据库**
```python
# 解析 AllPrintings.json
import json
with open('AllPrintings.json', 'r') as f:
    data = json.load(f)
    # 导入到自定义数据库
```

### 2. 与规则系统集成

- 使用 `keywords` 字段关联规则系统中的关键词异能
- 使用 `text` 字段进行向量化搜索
- 使用 `rulings` 字段补充规则裁定信息

### 3. 性能优化

- **索引**: 对 `name`, `uuid`, `setCode` 建立索引
- **缓存**: 常用卡牌信息缓存到 Redis
- **分页**: 大数据量查询使用分页
- **异步**: 下载和解析使用异步处理

## 🚀 实施步骤

1. **Phase 1: 基础下载**
   - 下载 `AllPrintings.sqlite.gz`
   - 解压并验证数据
   - 测试基本查询

2. **Phase 2: 数据集成**
   - 创建卡牌查询 API
   - 关联关键词异能
   - 集成到现有规则查询系统

3. **Phase 3: 性能优化**
   - 添加索引和缓存
   - 优化查询性能
   - 实现增量更新

4. **Phase 4: 向量化**
   - 提取卡牌文本
   - 生成向量嵌入
   - 实现语义搜索

## 📌 注意事项

1. **数据更新频率**: MTGJSON 每周更新一次
2. **文件大小**: AllPrintings 系列文件较大，需要充足的磁盘空间
3. **内存需求**: 解析 JSON 需要较多内存（至少 2GB）
4. **网络带宽**: 下载大文件需要稳定的网络连接
5. **版本兼容**: 注意 MTGJSON 数据模型的版本变更

---

**结论**: 推荐使用 `AllPrintings.sqlite.gz` 作为主要数据源，配合 `Keywords.json` 和 `SetList.json`，这样可以快速集成且易于维护。
