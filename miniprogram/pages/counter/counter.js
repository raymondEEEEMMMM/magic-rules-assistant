// pages/counter/counter.js
const app = getApp()

Page({
  data: {
    format: '1v1',
    formats: [
      { key: 'solo', name: '单人', playerCount: 1, life: 20 },
      { key: '1v1', name: '1v1', playerCount: 2, life: 20 },
      { key: 'commander', name: '指挥官', playerCount: 4, life: 40 }
    ],
    currentFormatName: '1v1',
    playerCount: 2,
    initialLife: 20,
    players: [],
    coinResult: null,
    coinAnimating: false,
    isLightTheme: true
  },

  onLoad() {
    this.setData({ isLightTheme: true })
    this.initPlayers()
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 初始化玩家数据
  initPlayers() {
    const format = this.data.format
    const formats = this.data.formats
    const currentFormat = formats.find(f => f.key === format) || formats[0]
    const players = []
    for (let i = 0; i < currentFormat.playerCount; i++) {
      players.push({
        name: `玩家${i + 1}`,
        life: currentFormat.life
      })
    }
    // 单人模式重置法力池
    if (currentFormat.playerCount === 1) {
      this.setData({
        players,
        playerCount: currentFormat.playerCount,
        initialLife: currentFormat.life
      })
    } else {
      this.setData({
        players,
        playerCount: currentFormat.playerCount,
        initialLife: currentFormat.life
      })
    }
  },

  // 设置赛制
  setFormat(e) {
    const index = parseInt(e.detail.value)
    const formats = this.data.formats
    const selected = formats[index]
    this.setData({
      format: selected.key,
      currentFormatName: selected.name
    })
    this.initPlayers()
  },

  // 调整生命值
  adjustLife(e) {
    const { index, delta } = e.currentTarget.dataset
    const players = this.data.players
    players[index].life += delta

    // 生命值不能低于0
    if (players[index].life < 0) {
      players[index].life = 0
    }

    this.setData({ players })
  },

  // 重置所有
  resetAll() {
    wx.showModal({
      title: '重置',
      content: '确定要重置所有生命值吗？',
      success: (res) => {
        if (res.confirm) {
          this.initPlayers()
          this.setData({ coinResult: null })
          wx.showToast({ title: '已重置', icon: 'success' })
        }
      }
    })
  },

  // 投掷硬币
  flipCoin() {
    if (this.data.coinAnimating) return

    this.setData({ coinAnimating: true, coinResult: null })

    // 模拟硬币翻转动画
    let flips = 0
    const maxFlips = 10
    const flipInterval = setInterval(() => {
      flips++
      // 随机显示正面或反面
      const result = Math.random() > 0.5 ? '正面' : '反面'
      this.setData({ coinResult: result })

      if (flips >= maxFlips) {
        clearInterval(flipInterval)
        // 最终结果
        const finalResult = Math.random() > 0.5 ? '正面' : '反面'
        this.setData({ coinResult: finalResult, coinAnimating: false })

        // 显示最终结果
        wx.showToast({
          title: `硬币: ${finalResult}`,
          icon: 'none',
          duration: 2000
        })
      }
    }, 100)
  },

  // 返回
  goBack() {
    wx.navigateBack()
  }
})