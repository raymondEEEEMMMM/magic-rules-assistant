# 数据库文档

## 1. 数据库连接配置

### 1.1 环境说明

本项目使用 CloudBase MySQL 数据库存储 Magic: The Gathering 规则和关键词数据。根据运行环境的不同，使用不同的连接地址：

| 环境 | 连接地址 | 说明 |
|------|----------|------|
| 云函数 | 172.17.0.5:3306 | 内网地址，仅在云函数环境中可访问 |
| 本地调试 | sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com:27987 | 外网地址，用于本地开发调试 |

### 1.2 连接参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 数据库类型 | MySQL | Tencent Cloud CynosDB |
| 用户名 | mtgask | 数据库用户 |
| 数据库名 | mtgask-0a1904c329 | 数据库实例名称 |
| 字符集 | utf8mb4 | 支持完整 Unicode |

### 1.3 配置文件

#### 云函数配置 (cloudbaserc.json)

```json
{
  "MYSQL_HOST": "172.17.0.5",
  "MYSQL_PORT": "3306",
  "MYSQL_USER": "mtgask",
  "MYSQL_PASSWORD": "your_password_here",
  "MYSQL_DATABASE": "magic-rules-assistant-0a1904c329"
}
```

#### 本地调试配置 (.env.local)

```env
MYSQL_HOST=sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com
MYSQL_PORT=27987
MYSQL_USER=mtgask
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=magic-rules-assistant-0a1904c329
```

### 1.4 连接代码

自动环境检测逻辑：

```python
def _is_cloud_function(self):
    """检测是否在云函数环境中运行"""
    return bool(os.environ.get('SCF_FUNCTION_NAME'))

def _get_connection_params(self):
    """根据运行环境获取数据库连接参数"""
    if self._is_cloud_function():
        # 云函数环境：使用内网地址
        return {
            'host': os.environ.get('MYSQL_HOST'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER'),
            'password': os.environ.get('MYSQL_PASSWORD'),
            'database': os.environ.get('MYSQL_DATABASE'),
            'charset': 'utf8mb4'
        }
    else:
        # 本地调试：从 .env.local 读取外网地址
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))
        return {
            'host': os.getenv('MYSQL_HOST'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
            'charset': 'utf8mb4'
        }
```

---

## 2. 数据库元数据结构

### 2.1 数据表概览

| 表名 | 用途 | 记录数 |
|------|------|--------|
| rules | MTG 规则数据 | ~50 |
| keyword_abilities | 关键词异能数据 | ~19 |

---

### 2.2 rules 表

#### 2.2.1 表结构

```sql
CREATE TABLE rules (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    rule_number VARCHAR(100) NOT NULL COMMENT '规则编号',
    category VARCHAR(100) NOT NULL COMMENT '规则分类',
    subcategory VARCHAR(100) COMMENT '规则子分类',
    content TEXT NOT NULL COMMENT '规则内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_rule_number (rule_number),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 2.2.2 字段说明

| 字段名 | 类型 | 必填 | 说明 | 索引 |
|--------|------|------|------|------|
| id | INT | 是 | 主键，自增 | PRIMARY |
| rule_number | VARCHAR(100) | 是 | 规则编号（如 100.1, 702.1） | INDEX |
| category | VARCHAR(100) | 是 | 规则分类（如 Combat, Keywords） | INDEX |
| subcategory | VARCHAR(100) | 否 | 规则子分类 | - |
| content | TEXT | 是 | 规则详细内容 | - |
| created_at | TIMESTAMP | 否 | 创建时间 | - |
| updated_at | TIMESTAMP | 否 | 更新时间 | - |

#### 2.2.3 示例数据

```sql
-- 战斗相关规则
('100.1', 'Combat', NULL, '100.1. Each turn has a combat phase...', NOW(), NOW())

-- 关键词异能规则
('702.1', 'Keywords', 'Flying', '702.1. Most abilities describe exactly what...', NOW(), NOW())
```

#### 2.2.4 常见查询示例

```sql
-- 查询特定类别的所有规则
SELECT * FROM rules WHERE category = 'Combat';

-- 查询特定子分类的规则
SELECT * FROM rules WHERE subcategory = 'Flying';

-- 模糊搜索规则内容
SELECT * FROM rules WHERE content LIKE '%combat damage%';

-- 查询特定规则编号
SELECT * FROM rules WHERE rule_number = '100.1';
```

---

### 2.3 keyword_abilities 表

#### 2.3.1 表结构

```sql
CREATE TABLE keyword_abilities (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '关键词名称',
    description TEXT NOT NULL COMMENT '关键词描述',
    category VARCHAR(50) COMMENT '关键词分类',
    related_rules TEXT COMMENT '关联的规则编号，JSON数组格式',
    examples TEXT COMMENT '使用示例，JSON数组格式',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 2.3.2 字段说明

| 字段名 | 类型 | 必填 | 说明 | 索引 |
|--------|------|------|------|------|
| id | INT | 是 | 主键，自增 | PRIMARY |
| name | VARCHAR(100) | 是 | 关键词名称（唯一） | UNIQUE, INDEX |
| description | TEXT | 是 | 关键词描述 | - |
| category | VARCHAR(50) | 否 | 关键词分类（如 Evasion, Combat） | INDEX |
| related_rules | TEXT | 否 | 关联的规则编号（JSON数组） | - |
| examples | TEXT | 否 | 使用示例（JSON数组） | - |
| created_at | TIMESTAMP | 否 | 创建时间 | - |
| updated_at | TIMESTAMP | 否 | 更新时间 | - |

#### 2.3.3 示例数据

```sql
-- 飞行异能
('Flying', 'Flying is an evasion ability...', 'Evasion', 
 '["702.9"]', 
 '[{ "text": "This creature can''t be blocked except by creatures with flying or reach." }]', 
 NOW(), NOW())

-- 先攻异能
('First Strike', 'First strike is a combat ability...', 'Combat',
 '["702.7"]',
 '[{ "text": "This creature deals combat damage before creatures without first strike." }]',
 NOW(), NOW())
```

#### 2.3.4 常见查询示例

```sql
-- 查询所有关键词
SELECT * FROM keyword_abilities;

-- 查询特定分类的关键词
SELECT * FROM keyword_abilities WHERE category = 'Evasion';

-- 搜索关键词名称
SELECT * FROM keyword_abilities WHERE name LIKE '%Fly%';

-- 查询关键词及其关联规则
SELECT 
    ka.name,
    ka.description,
    ka.related_rules,
    GROUP_CONCAT(r.rule_number) as rule_numbers
FROM keyword_abilities ka
LEFT JOIN rules r ON JSON_CONTAINS(ka.related_rules, JSON_QUOTE(r.rule_number))
GROUP BY ka.id;
```

---

## 3. 数据库操作指南

### 3.1 初始化数据库

创建表结构的 SQL 文件：`/Users/lianghaoming/cbworkplace/init_mysql.sql`

```bash
# 使用 Python MCP 工具执行初始化
python init_mysql.py
```

### 3.2 本地测试

使用本地配置文件测试数据库连接：

```bash
# 测试连接
python test_mysql_connection.py

# 测试数据库查询
python test_local_database.py
```

### 3.3 数据导入

批量导入数据到 MySQL：

```python
# 参见 backend/database_mysql.py 中的 import_rules() 方法
# 或使用 MCP executeWriteSQL 工具
```

---

## 4. 维护指南

### 4.1 环境变量管理

- **云函数环境**：修改 `cloudbaserc.json`，部署后自动生效
- **本地调试**：修改 `.env.local`，确保不要提交到版本控制

### 4.2 数据备份

定期备份数据库结构和数据：

```sql
-- 导出表结构
mysqldump -h <host> -u <user> -p --no-data <database> > schema.sql

-- 导出数据
mysqldump -h <host> -u <user> -p <database> > backup.sql
```

### 4.3 性能优化

- 已为常用查询字段创建索引（rule_number, category, name）
- 使用 InnoDB 引擎支持事务
- 使用 utf8mb4 字符集支持完整 Unicode

### 4.4 安全注意事项

- ⚠️ 数据库密码不应硬编码在代码中
- ⚠️ `.env.local` 文件应添加到 `.gitignore`
- ⚠️ 生产环境应使用更安全的密码管理方案

---

## 5. 相关文件

| 文件路径 | 说明 |
|----------|------|
| `functions/magic-rules-api/backend/database.py` | 数据库连接和查询主模块 |
| `functions/magic-rules-api/backend/database_mysql.py` | MySQL 专用数据库模块 |
| `functions/magic-rules-api/backend/.env.local` | 本地调试配置 |
| `cloudbaserc.json` | 云函数环境配置 |
| `init_mysql.sql` | 数据库初始化 SQL |
| `init_mysql.py` | 数据库初始化脚本 |
| `test_mysql_connection.py` | MySQL 连接测试 |
| `test_local_database.py` | 本地数据库查询测试 |

---

## 6. 版本历史

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-03-14 | 1.0 | 初始版本，创建 rules 和 keyword_abilities 表，实现自动环境检测 |
