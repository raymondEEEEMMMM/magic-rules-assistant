// pages/token-generate/token-generate.js
const app = getApp()

Page({
  data: {
    isLightTheme: false,
    card: null,
    tokenCount: 1,
    isVertical: false,
    cardRotations: {}
  },

  onLoad(options) {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    if (options.card) {
      try {
        const card = JSON.parse(decodeURIComponent(options.card))
        this.setData({ card: card })
      } catch (e) {
        wx.showToast({ title: '参数错误', icon: 'none' })
      }
    }
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  goBack() {
    wx.navigateBack()
  },

  minusCount() {
    if (this.data.tokenCount > 1) {
      this.setData({ tokenCount: this.data.tokenCount - 1 })
    }
  },

  plusCount() {
    if (this.data.tokenCount < 27) {
      this.setData({ tokenCount: this.data.tokenCount + 1 })
    }
  },

  toggleRotate() {
    this.setData({ isVertical: !this.data.isVertical })
  },

  // 点击卡图横置/竖置（90度旋转）
  toggleCardRotate(e) {
    const index = e.currentTarget.dataset.index
    const rotationKey = `cardRotations[${index}]`
    const current = this.data.cardRotations?.[index] || 0
    this.setData({
      cardRotations: {
        ...this.data.cardRotations,
        [index]: current === 0 ? 90 : 0
      }
    })
  },

  previewToken() {
    if (!this.data.card) return
    const imageUrl = this.data.card.image_uris
      ? (this.data.card.image_uris.normal || this.data.card.image_uris.small)
      : null
    if (imageUrl) {
      wx.previewImage({
        urls: [imageUrl]
      })
    }
  }
})
