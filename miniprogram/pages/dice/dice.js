// pages/dice/dice.js
const app = getApp()

Page({
  data: {
    isLightTheme: false,
    // 骰子
    selectedDice: 20,
    diceOptions: [
      { value: 20, label: 'D20' },
      { value: 12, label: 'D12' },
      { value: 10, label: 'D10' },
      { value: 8, label: 'D8' },
      { value: 6, label: 'D6' },
      { value: 4, label: 'D4' }
    ],
    customSides: 20,
    isCustom: false,
    diceResult: null,
    isRolling: false,
    // 随机选卡
    drawCount: 1,
    drawnCards: [],
    isDrawing: false,
    // 丢硬币
    coinResult: null,
    coinAnimating: false
  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 返回
  goBack() {
    wx.navigateBack()
  },

  // 选择骰子类型
  selectDice(e) {
    const value = parseInt(e.currentTarget.dataset.value)
    this.setData({
      selectedDice: value,
      isCustom: false,
      diceResult: null
    })
  },

  // 切换自定义
  toggleCustom() {
    this.setData({
      isCustom: !this.data.isCustom,
      diceResult: null
    })
  },

  // 输入自定义面数
  inputCustomSides(e) {
    const sides = parseInt(e.detail.value) || 20
    this.setData({ customSides: sides })
  },

  // 掷骰子
  rollDice() {
    if (this.data.isRolling) return

    const sides = this.data.isCustom ? this.data.customSides : this.data.selectedDice
    if (sides < 2) {
      wx.showToast({ title: '面数至少为2', icon: 'none' })
      return
    }

    this.setData({ isRolling: true, diceResult: null })

    // 模拟掷骰动画
    let rollCount = 0
    const maxRolls = 15
    const rollInterval = setInterval(() => {
      const result = Math.floor(Math.random() * sides) + 1
      this.setData({ diceResult: result })
      rollCount++

      if (rollCount >= maxRolls) {
        clearInterval(rollInterval)
        const finalResult = Math.floor(Math.random() * sides) + 1
        this.setData({ diceResult: finalResult, isRolling: false })
        wx.vibrateShort({ type: 'heavy' })
      }
    }, 80)
  },

  // 设置抽卡数量
  setDrawCount(e) {
    const count = parseInt(e.detail.value) || 1
    this.setData({ drawCount: Math.max(1, Math.min(count, 20)) })
  },

  minusDrawCount() {
    this.setData({ drawCount: Math.max(1, this.data.drawCount - 1) })
  },

  plusDrawCount() {
    this.setData({ drawCount: Math.min(20, this.data.drawCount + 1) })
  },

  // 随机选卡（从 Scryfall 抽卡包）
  drawCards() {
    if (this.data.isDrawing) return

    this.setData({ isDrawing: true, drawnCards: [] })

    // 随机选一个系列
    const sets = ['znr', 'mid', 'vow', 'neo', 'snc', 'dmu', 'bro', 'one', 'mom', 'mat']
    const randomSet = sets[Math.floor(Math.random() * sets.length)]
    const count = this.data.drawCount

    wx.request({
      url: `https://api.scryfall.com/cards/random`,
      success: res => {
        if (res.data && res.data.image_uris) {
          const cards = [{
            name: res.data.name,
            image: res.data.image_uris.normal || res.data.image_uris.small,
            set: res.data.set_name
          }]
          this.setData({ drawnCards: cards, isDrawing: false })
        } else {
          this.setData({ isDrawing: false })
          wx.showToast({ title: '获取失败', icon: 'none' })
        }
      },
      fail: () => {
        this.setData({ isDrawing: false })
        wx.showToast({ title: '网络错误', icon: 'none' })
      }
    })
  },

  // 丢硬币
  flipCoin() {
    if (this.data.coinAnimating) return

    this.setData({ coinAnimating: true, coinResult: null })

    let flips = 0
    const maxFlips = 10
    const flipInterval = setInterval(() => {
      flips++
      const result = Math.random() > 0.5 ? '正面' : '反面'
      this.setData({ coinResult: result })

      if (flips >= maxFlips) {
        clearInterval(flipInterval)
        const finalResult = Math.random() > 0.5 ? '正面' : '反面'
        this.setData({ coinResult: finalResult, coinAnimating: false })
        wx.vibrateShort({ type: 'heavy' })
      }
    }, 100)
  }
})