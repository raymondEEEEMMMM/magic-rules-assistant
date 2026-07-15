// pages/setcards/setcards.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    setCode: '',
    setName: '',
    setInfo: null,
    cards: [],
    loading: false,
    loaded: false,
    isLightTheme: true
  },

  onLoad(options) {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    if (options.setCode) {
      this.setData({
        setCode: options.setCode,
        setName: options.setName ? decodeURIComponent(options.setName) : ''
      })
      this.loadSetData()
    }
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 更新主题（由 app.js 调用）
  updateTheme(isLight) {
    this.setData({ isLightTheme: isLight })
  },

  // 返回
  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  goToIndex() {
    wx.navigateBack({
      fail: () => {
        wx.switchTab({ url: '/pages/index/index' })
      }
    })
  },

  // 加载系列数据
  loadSetData() {
    const { setCode, setName } = this.data
    this.setData({ loading: true })

    api.getSetCards(setCode, 1, 9999).then(res => {
      const cards = (res.items || []).map(card => ({
        id: card.id,
        display_name: card.display_name || card.name || '',
        name: card.name || '',
        zhs_name: card.zhs_name || card.display_name || card.name || '',
        image_uris: card.image_uris || null,
        image_url: card.image_url || '',
        colors: card.colors || [],
        cmc: card.cmc || 0,
        type_line: card.type_line || '',
        rarity: card.rarity || '',
        mana_cost: card.mana_cost || ''
      }))

      this.setData({
        cards,
        setInfo: {
          name: setName,
          code: setCode,
          iconUrl: `https://svgs.scryfall.io/sets/${setCode.toLowerCase()}.svg`
        },
        loading: false,
        loaded: true
      })
    }).catch(err => {
      this.setData({
        loading: false,
        loaded: true
      })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    if (!cardId) return
    const url = `/pages/card/card?id=${encodeURIComponent(cardId)}`
    wx.navigateTo({ url })
  },

  // 新版 WXML 调用
  onCardTap(e) {
    this.viewCardDetail(e)
  }
})
