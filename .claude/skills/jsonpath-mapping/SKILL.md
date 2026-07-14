---
name: jsonpath-mapping
description: JSONPATH 规则引擎 - 从数据池反推接口映射的方法论。用于分析数据池结构、理解字段关系、创建和维护接口映射文件。
---

## 核心概念

### 数据流

```
后端数据 → 接口映射（字段翻译） → 数据池（业务友好字段） → 规则（$JP{{ $.字段名 }}）
```

**关键理解**：接口映射描述的是"数据池字段 → 原始后端字段"的映射关系。但山东地区数据池已经是业务友好的中文字段名，规则直接引用，不需要额外映射。

### 三种语法

| 语法 | 地区 | 示例 |
|-----|------|------|
| `$JP{{ $.字段名 }}` | 新规则（推荐） | `var x = $JP{{ $.转账支付金额 }};` |
| `$JP['字段名']` | 冀北-结算（规则集合.js） | `var x = $JP['支付金额'];` |
| `JSONPath.JSONPath({ path: '$.xxx' })` | 山东-结算（旧规则） | `var x = JSONPath.JSONPath({ path: '$.其他附件', ... });` |

---

## 反推方法论

### 步骤一：读取数据池，理解顶层字段

数据池 JSON 顶层字段就是规则可以直接引用的字段。

```bash
# 列出数据池所有顶层字段（排除 sys. 和空对象）
node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('<数据池路径>', 'utf-8'));
for (const [k,v] of Object.entries(data)) {
  if (k.startsWith('sys.')) continue;
  if (v !== null && typeof v === 'object' && Object.keys(v).length === 0) continue;
  console.log(k + ': ' + JSON.stringify(v).slice(0,60));
}
"
```

### 步骤二：分析深层结构（发票、附件等）

发票结构和附件是最复杂的嵌套：

```bash
# 展开发票结构
node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('<数据池路径>', 'utf-8'));
const inv = data['发票结构'];
// 第一层
console.log('发票结构[0] keys:', Object.keys(inv[0]).join(', '));
// 电子凭证字段
const elec = inv.find(i => i.invoicesJson[0].XbrlConfigId);
if (elec) console.log('电子凭证 keys:', Object.keys(elec.invoicesJson[0]).join(', '));
// 非电子凭证字段
const non = inv.find(i => !i.invoicesJson[0].XbrlConfigId);
if (non) console.log('非电子凭证 keys:', Object.keys(non.invoicesJson[0]).join(', '));
"
```

### 步骤三：对照规则引用的字段

```bash
# 从规则文件提取所有 $JP{{ $.xxx }} 引用
grep -rho '\$JP{{ \$\.[^ }]* }}' 具体规则实现/<地区>/1接口映射/*.js | sort -u
```

### 步骤四：检查接口映射覆盖情况

运行 `反推接口映射.js` 生成报告：

```bash
node 反推接口映射.js <地区> [子场景]
# 示例
node 反推接口映射.js 福建-结算 物资采购
node 反推接口映射.js 福建-结算 融资
node 反推接口映射.js 冀北-结算
node 反推接口映射.js 山东-结算
node 反推接口映射.js 河北-配比
```

---

## 各地区特点

### 福建-结算

- **接口映射**：`接口映射_物资采购.json`、`接口映射_融资.json` 分开
- **数据池**：字段已是业务友好名（`转账子表_业务类型`、`单据_结算信息子表_核销预付款`）
- **后端原始路径**：映射值指向 `ywBillData.JSXX[0].ADV_PML_AMT` 等嵌套路径
- **注意**：融资场景和物资采购场景字段不同，规则混用会导致"缺失映射"

### 冀北-结算

- **接口映射**：`接口映射.json`（17个字段）
- **数据池**：有 `单据数据` 子对象，包含 `GENERBILLISTAT_PAY_DET` 等原始后端字段
- **问题**：`appPmtAmt`、`pmtUnit` 等映射目标不在数据池顶层（是后端系统的字段名）
- **注意**：`预计付款日期` 映射值是 JS 表达式而非简单字段路径

### 河北-配比

- **接口映射**：`接口映射.json`（33个字段）
- **数据池**：53个顶层字段（含大量 `null` 值字段）
- **问题**：`预计付款日期` 映射值是 JS 表达式；23个数据池字段无映射
- **命名**：使用英文字段名（如 `pubToPriv`、`payPlanNo`）

### 山东-结算

- **无传统接口映射**：数据池字段已是业务友好名，规则直接引用
- **规则文件**：`进度款付款校验.js`、`质保金付款校验.js`
- **`山东运算接口.json`**：是规则合集（类似其他地区的 `规则集合.js`），不是接口映射
- **已创建**：`接口映射.json`（文档化19个字段）+ `字段结构说明.md`

### 冀北-配比

- 最简单，只有 `运算接口.json` 和 `接口映射.json`
- 1条规则，无大模型规则

---

## 创建接口映射文件

### 标准模板

```json
{
  "业务字段名": "$.数据池字段路径",
  "发票结构": "$.发票结构",
  "转账支付金额": "$.转账支付金额",
  "其他附件": "$.其他附件"
}
```

### 发票结构特殊处理

发票数据根据 `XbrlConfigId` 判断类型：

```json
{
  "发票_含税金额_电子凭证": "$.发票结构[*].invoicesJson[?(@.XbrlConfigId)].TotalTax-includedAmount",
  "发票_含税金额_非电子凭证": "$.发票结构[*].invoicesJson[?(@.XbrlConfigId==null)].amouInTot"
}
```

---

## 工具脚本

`/Users/lianghaoming/.openclaw/workspace_ygsoft/JSONPATH/反推接口映射.js`

```bash
node 反推接口映射.js <地区> [子场景]
```

输出：
- `*_字段清单.md` — 所有字段路径和示例值
- `*_接口映射草稿.md` — 可填入的映射模板
- 控制台打印摘要（映射覆盖情况、缺失字段）

---

## 常见问题排查

### Q：接口映射有值但数据池找不到对应字段
**A**：映射目标是后端原始字段名，不在数据池中。这是正常现象——接口映射描述的是"如果规则需要从原始数据取，映射到哪里"，而不是"数据池里有什么"。

### Q：规则引用 `$.单据数据.XXX` 但数据池没有 `单据数据` 子对象
**A**：说明该数据池可能是经过预处理的，部分后端字段已经被提取为顶层字段。需要对照原始后端接口确认。

### Q：福建-融资 规则引用了物资采购的字段
**A**：这是配置问题。融资场景应使用 `接口映射_融资.json`，需要检查规则文件是否按场景正确分离。

### Q：`预计付款日期` 的映射值是 JS 代码而非字段路径
**A**：这是历史遗留格式。正确做法是 `预计付款日期` 映射到 `estPayDate` 字段，由规则代码负责时间戳转换。
