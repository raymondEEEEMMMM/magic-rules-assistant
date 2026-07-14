// pages/devlog/devlog.js
const app = getApp()

Page({
  data: {
    isLightTheme: true,
    devlogData: [
      {
        version: 'v1.3.0',
        date: '2026-04-16',
        items: [
          { type: 'feat', content: 'Promo 卡快讯功能上线，随时了解最新促销卡牌资讯' },
        ]
      },
      {
        version: 'v1.2.0',
        date: '2026-04-16',
        items: [
          { type: 'feat', content: 'URL导入增加format解析' },
          { type: 'fix', content: '修复deck API路由未注册和数据库冗余列问题' },
          { type: 'perf', content: '套牌管理API完善' }
        ]
      },
      {
        version: 'v1.1.0',
        date: '2026-04-15',
        items: [
          { type: 'feat', content: 'AI裁判功能上线，智能规则问答' },
          { type: 'feat', content: '套牌管理功能（导入、导出、增删改查）' },
          { type: 'feat', content: '骰子 & 随机功能' },
          { type: 'feat', content: 'Token生成器' },
          { type: 'feat', content: 'Odds计算器' },
          { type: 'fix', content: '修复Scryfall API访问问题' },
          { type: 'fix', content: '修复Token搜索400错误' }
        ]
      },
      {
        version: 'v1.0.0',
        date: '2026-04-10',
        items: [
          { type: 'feat', content: 'SLD专区页面上线' },
          { type: 'feat', content: '首页最新系列资讯展示' },
          { type: 'feat', content: '卡牌详情页优化' },
          { type: 'perf', content: '搜索功能优化' }
        ]
      }
    ]
  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 返回首页
  goToIndex() {
    wx.redirectTo({ url: '/pages/index/index' })
  }
})