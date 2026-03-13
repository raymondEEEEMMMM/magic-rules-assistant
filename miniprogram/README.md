# 万智牌规则助手 - 微信小程序

基于云开发的万智牌规则查询小程序。

## 功能特性

- 🔍 **规则搜索** - 输入关键词搜索相关游戏规则
- 📖 **关键词查询** - 查询卡牌异能的详细规则解释  
- 🃏 **卡牌查询** - 搜索卡牌并查看详细信息
- 🎲 **随机卡牌** - 每日随机展示一张卡牌

## 项目结构

```
miniprogram/
├── app.js              # 小程序入口
├── app.json            # 小程序配置
├── app.wxss            # 全局样式
├── project.config.json # 项目配置
├── sitemap.json        # SEO配置
├── pages/
│   ├── index/          # 首页
│   ├── search/         # 综合搜索
│   ├── card/          # 卡牌查询
│   ├── keyword/       # 关键词查询
│   └── rule/          # 规则搜索
├── utils/
│   └── api.js          # API封装
└── images/             # 图片资源
```

## 快速开始

### 1. 微信开发者工具

1. 下载微信开发者工具：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. 打开项目目录
3. 修改 `app.js` 中的云环境ID

### 2. 配置API地址

在 `app.js` 中修改：

```javascript
wx.cloud.init({
  env: 'your-cloud-env-id', // 替换为您的云环境ID
  traceUser: true
})
```

## 页面预览

### 首页
- 快速功能入口
- 热门关键词标签
- 今日随机卡牌

### 搜索页
- 综合搜索框
- 分类筛选（全部/规则/关键词/卡牌）
- 搜索历史记录

### 卡牌页
- 卡牌名称搜索
- 卡牌列表展示
- 卡牌详情弹窗

### 关键词页
- 关键词搜索
- 规则解释展示
- 示例说明

## 开发指南

### 添加新页面

1. 在 `app.json` 中注册页面
2. 创建页面目录和文件
3. 实现页面逻辑

### 调用API

```javascript
const app = getApp()

// 调用云函数
app.requestApi('/api/search', { q: '战斗' })
  .then(res => {
    console.log(res)
  })
```

## 技术栈

- 微信小程序原生开发
- 腾讯云开发 CloudBase
- 云函数 API 服务

## 相关文档

- [微信小程序文档](https://developers.weixin.qq.com/miniprogram/dev/)
- [CloudBase 文档](https://docs.cloudbase.net/)
- [MTGCH API](https://mtgch.com/api/v1/docs)
