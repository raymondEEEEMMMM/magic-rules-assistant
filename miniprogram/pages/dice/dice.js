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
  goToIndex() {
    wx.redirectTo({ url: '/pages/index/index' })
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