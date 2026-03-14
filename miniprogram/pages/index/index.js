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

  // 跳转关键词测试页面
  goToKeywordTest() {
    wx.navigateTo({
      url: '/pages/test/test'
    })
  },

  // 跳转API测试页面
  goToApiTest() {
    wx.navigateTo({
      url: '/pages/apitest/apitest'
    })
  },

  // 自动化测试系命异能
  autoTestLifelink() {
    wx.showModal({
      title: '自动化测试',
      content: '将自动测试点击关键词查询系命异能的完整流程',
      confirmText: '开始测试',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: '/pages/keyword/keyword?autoTest=true'
          })
        }
      }
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
    
    // 模拟随机卡牌数据
    setTimeout(() => {
      wx.hideLoading()
      const mockCards = [
        {
          name: '黑绿霸主',
          manaCost: '{2}{B}{G}',
          type: '生物 — 霸主',
          text: '当黑绿霸主进入战场时，你可以从你的牌库中寻找一张沼泽牌或森林牌，将其横置放进战场，然后将你的牌库洗牌。',
          power: '4',
          toughness: '4'
        },
        {
          name: '红蓝法师',
          manaCost: '{U}{R}',
          type: '生物 — 人类 法师',
          text: '飞行\n每当红蓝法师成为咒语或异能的目标时，你可以掷硬币。如果是正面，反击该咒语或异能。',
          power: '2',
          toughness: '2'
        },
        {
          name: '白绿野兽',
          manaCost: '{3}{G}{W}',
          type: '生物 — 野兽',
          text: '践踏\n每当白绿野兽造成战斗伤害时，你可以获得等量的生命。',
          power: '5',
          toughness: '5'
        }
      ]
      
      const randomCard = mockCards[Math.floor(Math.random() * mockCards.length)]
      wx.navigateTo({
        url: `/pages/card/card?card=${encodeURIComponent(JSON.stringify(randomCard))}`
      })
    }, 500)
  }
})
