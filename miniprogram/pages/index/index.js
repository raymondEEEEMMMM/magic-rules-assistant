// pages/index/index.js
const app = getApp()

// API 配置
const API_BASE = 'https://magic-rules-assistant-0a1904c329.tcb.qcloud.la'

Page({
  data: {
    hotKeywords: [
      'Flying', 'Trample', 'Deathtouch', 'First strike', 'Lifelink'
    ]
  },

  onLoad() {
    // 页面加载
  },

  // 跳转关键词页面
  goToKeyword() {
    wx.navigateTo({
      url: '/pages/keyword/keyword'
    })
  },

  // 跳转卡牌页面
  goToCard() {
    wx.navigateTo({
      url: '/pages/card/card'
    })
  },

  // 跳转搜索页面
  goToSearch() {
    wx.navigateTo({
      url: '/pages/search/search'
    })
  },

  // 跳转 AI 裁判页面
  goToAIJudge() {
    wx.navigateTo({
      url: '/pages/agent/agent'
    })
  },

  // 搜索关键词
  searchKeyword(e) {
    const keyword = e.currentTarget.dataset.keyword
    wx.navigateTo({
      url: `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    })
  },

  // 跳转 API 测试页面
  goToAPITest() {
    wx.navigateTo({
      url: '/pages/apitest/apitest'
    })
  }
})
