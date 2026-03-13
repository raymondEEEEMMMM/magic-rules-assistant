# MTG 卡牌数据集成说明

## 📋 集成方案概述

我们采用 **"外部 SQLite + 内部集成"** 的混合方案，将 MTGJSON 数据无缝集成到现有规则系统。

### 🏗️ 架构设计

```
data/
├── magic_rules.db              # 现有规则数据库（我们维护）
│   ├── rules                   # 综合规则
│   ├── keyword_abilities       # 关键词异能
│   ├── card_rules             # 卡牌规则（自定义）
│   └── qa_templates           # 问答模板
│
├── mtg/
│   ├── AllPrintings.sqlite    # MTGSQLite 数据库（外部，无需修改）
│   ├── Keywords.json          # 关键词异能定义
│   └── SetList.json           # 系列列表
│
└── rules/
    └── MagicCompRules*.txt     # 完整规则文件
```

### 💡 方案优势

| 优势 | 说明 |
|------|------|
| ✅ **零冗余** | MTGSQLite 保持原样，不重复存储数据 |
| ✅ **快速查询** | 直接查询 MTGSQLite，性能最优 |
| ✅ **易于更新** | 下载新的 SQLite 文件即可，无需数据迁移 |
| ✅ **统一接口** | 通过 CardService 封装，对上层透明 |
| ✅ **灵活扩展** - 可随时添加自定义卡牌规则到 magic_rules.db |

---

## 🚀 快速开始

### 1. 下载卡牌数据

```bash
# 下载所有必需文件
python3 download_cards.py
```

下载内容包括：
- `AllPrintings.sqlite.gz` → 解压为 `AllPrintings.sqlite`（~200-300MB）
- `Keywords.json`（~10-50KB）
- `SetList.json`（~20-50KB）

### 2. 测试卡牌查询

```bash
# 运行测试脚本
python3 test_card_service.py
```

### 3. 在代码中使用

```python
from services import CardService

# 创建服务实例
card_service = CardService()

# 按名称搜索卡牌
cards = card_service.search_cards_by_name("Black Lotus", limit=5)

# 按关键词异能搜索
cards = card_service.search_cards_by_keywords(["Flying", "Trample"], limit=10)

# 获取卡牌统计信息
stats = card_service.get_statistics()

# 获取向量化数据
cards = card_service.get_card_text_for_vectorization(limit=100)

# 关闭连接
card_service.close()
```

---

## 📊 API 参考

### CardService 类

#### 搜索方法

##### `search_cards_by_name(name: str, limit: int = 5) -> List[Dict]`

按卡牌名称搜索（支持模糊匹配）

**参数：**
- `name`: 卡牌名称
- `limit`: 返回结果数量限制（默认 5）

**返回：**
```python
[
    {
        "name": "Black Lotus",
        "type": "Artifact",
        "text": "{T}, Sacrifice Black Lotus: Add three mana of any one color.",
        "colors": [],
        "mana_cost": "{0}",
        "uuid": "9a814c89-c858-4db6-bc58-6373c636d353",
        "set_code": "LEA"
    }
]
```

##### `get_card_by_uuid(uuid: str) -> Optional[Dict]`

根据 UUID 获取卡牌

**参数：**
- `uuid`: 卡牌的唯一标识符

**返回：** 卡牌信息字典或 None

##### `search_cards_by_keywords(keywords: List[str], limit: int = 10) -> List[Dict]`

根据关键词异能搜索卡牌

**参数：**
- `keywords`: 关键词异能列表（如 ["Flying", "Trample"]）
- `limit`: 返回结果数量限制（默认 10）

**返回：** 卡牌列表

#### 元数据方法

##### `get_keywords_list() -> List[str]`

获取所有关键词异能列表

**返回：** 关键词名称列表

```python
["Flying", "Trample", "First Strike", "Haste", ...]
```

##### `get_statistics() -> Dict`

获取数据库统计信息

**返回：**
```python
{
    "total_cards": 27000,
    "total_sets": 500,
    "database_size_mb": 245.6,
    "database_path": "/path/to/AllPrintings.sqlite"
}
```

#### 向量化方法

##### `get_card_text_for_vectorization(limit: int = 100) -> List[Dict]`

获取适合向量化的卡牌数据

**参数：**
- `limit`: 返回卡牌数量限制

**返回：**
```python
[
    {
        "id": "uuid",
        "name": "Card Name",
        "type": "Creature",
        "text": "Card text...",
        "colors": ["B"],
        "mana_cost": "{1}{B}"
    },
    ...
]
```

---

## 🔗 与规则系统集成

### 方式一：在 RuleService 中集成卡牌查询

```python
from services import RuleService, CardService

class RuleService:
    def __init__(self, db):
        self.db = db
        self.card_service = CardService()  # 添加卡牌服务

    def search_with_cards(self, query: str):
        """同时搜索规则和卡牌"""
        # 搜索规则
        rules = self.search(query)

        # 搜索卡牌
        cards = self.card_service.search_cards_by_name(query, limit=3)

        return {
            "rules": rules,
            "cards": cards
        }
```

### 方式二：在微信 Handler 中集成

```python
from wechat import MessageHandler
from services import CardService

class MessageHandler:
    def __init__(self, rule_service):
        self.rule_service = rule_service
        self.card_service = CardService()  # 添加卡牌服务

    def handle_message(self, user_message: str):
        # 检测卡牌查询
        if user_message.startswith("卡牌:"):
            card_name = user_message[3:].strip()
            cards = self.card_service.search_cards_by_name(card_name)
            return self._format_cards(cards)

        # 其他逻辑...
```

---

## 📈 数据统计

### MTGSQLite 数据规模

| 指标 | 数量 |
|------|------|
| 总卡牌数 | ~27,000+ |
| 系列数 | ~500+ |
| 数据库大小 | ~200-300MB |
| 关键词异能 | ~190+ |

### 查询性能

- **名称搜索**: < 50ms（索引查询）
- **关键词搜索**: < 100ms（LIKE 查询）
- **批量获取**: < 200ms（100 条记录）

---

## 🎯 使用场景

### 1. 卡牌规则查询

用户输入卡牌名，系统返回：
- 卡牌基本信息和规则文本
- 相关的关键词异能解释
- 官方裁定（如有）

### 2. 关键词异能查询

用户输入关键词，系统返回：
- 关键词异能定义
- 具有该异能的卡牌列表
- 相关规则条目

### 3. 复杂场景分析

用户描述复杂场景，系统：
- 查找涉及的卡牌
- 分析卡牌异能
- 关联规则解释

### 4. 向量化搜索

用于第二阶段 AI 问答：
- 将卡牌文本向量化
- 语义搜索相关卡牌
- 智能推荐

---

## 🔧 维护和更新

### 更新卡牌数据

```bash
# 方式一：强制重新下载
python3 download_cards.py

# 方式二：使用 CardDownloader
from services import CardDownloader

downloader = CardDownloader()
result = downloader.download_all(force=True)
```

### 数据版本控制

MTGJSON 每月更新一次，建议：
- 定期检查更新（通过 API 获取版本信息）
- 下载新版本后，自动备份旧版本
- 更新完成后通知用户

### 性能优化建议

1. **添加查询缓存**
   - 缓存常用卡牌查询结果
   - 设置合理的过期时间

2. **使用连接池**
   - CardService 使用连接池管理数据库连接
   - 避免频繁开关连接

3. **批量查询优化**
   - 一次查询多张卡牌
   - 减少数据库访问次数

---

## 🐛 故障排查

### 问题：找不到数据库

**错误信息：** `未找到 MTGSQLite 数据库`

**解决方案：**
```bash
# 1. 检查文件是否存在
ls -lh data/mtg/AllPrintings.sqlite

# 2. 重新下载数据
python3 download_cards.py

# 3. 检查路径配置
python3 -c "from services import CardService; c = CardService(); print(c._get_db_path())"
```

### 问题：查询超时

**错误信息：** `查询超时`

**解决方案：**
- 减少查询结果数量（limit 参数）
- 添加数据库索引
- 使用批量查询代替多次单次查询

### 问题：中文乱码

**错误信息：** 中文显示为乱码

**解决方案：**
- 确保使用 UTF-8 编码
- 检查数据库连接编码设置

---

## 📚 相关文档

- [MTGJSON 官方文档](https://mtgjson.com/)
- [MTGJSON 数据模型](https://mtgjson.com/data-models/)
- [MTG卡牌数据需求分析](./MTGJSON卡牌数据需求分析.md)
- [规则下载功能说明](./规则下载功能说明.md)

---

## 🎉 总结

通过 CardService 和 CardDownloader，我们成功实现了：

✅ **完整的卡牌数据** - 27,000+ 张卡牌
✅ **高性能查询** - SQLite 直接查询，速度快
✅ **易于集成** - 统一的 API 接口
✅ **灵活扩展** - 支持自定义规则和向量化
✅ **自动化更新** - 支持定时下载新数据

现在可以开始将卡牌数据集成到规则问答系统了！
