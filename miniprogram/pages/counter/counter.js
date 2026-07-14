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
    isLightTheme: true,
    // Mana tracking (solo mode)
    manaColors: ['W', 'U', 'B', 'R', 'G', 'C'],
    manaPool: { W: 0, U: 0, B: 0, R: 0, G: 0, C: 0 },
    showMana: false
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
          wx.showToast({ title: '已重置', icon: 'success' })
        }
      }
    })
  },

  // 返回
  goToIndex() {
    wx.redirectTo({ url: '/pages/index/index' })
  },

  // 切换 Mana Bar 显示
  toggleMana() {
    this.setData({ showMana: !this.data.showMana })
  },

  // 调整法力值
  adjustMana(e) {
    const { color, delta } = e.currentTarget.dataset
    const manaPool = this.data.manaPool
    manaPool[color] += delta
    if (manaPool[color] < 0) manaPool[color] = 0
    this.setData({ manaPool })
  },

  // 重置法力池
  resetMana() {
    const manaPool = { W: 0, U: 0, B: 0, R: 0, G: 0, C: 0 }
    this.setData({ manaPool })
  }
})