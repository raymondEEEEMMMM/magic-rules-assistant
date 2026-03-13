// pages/index/index.js
const app = getApp()

Page({
  data: {
    hotKeywords: [
      '飞行', '警戒', '死触', '闪现', '敏捷', 
      '连击', '毁坏', '先攻', '瞬息', '辟邪'
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

  // 跳转规则页面
  goToRule() {
    wx.navigateTo({
      url: '/pages/rule/rule'
    })
  },

  // 跳转卡牌页面
  goToCard() {
    wx.switchTab({
      url: '/pages/card/card'
    })
  },

  // 跳转搜索页面
  goToSearch() {
    wx.switchTab({
      url: '/pages/search/search'
    })
  },

  // 搜索关键词
  searchKeyword(e) {
    const keyword = e.currentTarget.dataset.keyword
    wx.navigateTo({
      url: `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    })
  },

  // 显示随机卡牌
  showRandomCard() {
    wx.showLoading({ title: '加载中...' })
    
    app.requestApi('/api/random')
      .then(res => {
        wx.hideLoading()
        if (res.result) {
          wx.navigateTo({
            url: `/pages/card/card?card=${encodeURIComponent(JSON.stringify(res.result))}`
          })
        }
      })
      .catch(err => {
        wx.hideLoading()
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      })
  }
})
