// pages/odds/odds.js
const app = getApp()

// 超几何分布概率计算
// P(X=k) = C(K,k) × C(N-K, n-k) / C(N,n)
// N = 套牌总张数, K = 目标牌数量, n = 手牌数量
function combinations(n, r) {
  if (r > n) return 0
  if (r === 0 || r === n) return 1
  let c = 1
  for (let i = 0; i < r; i++) {
    c = c * (n - i) / (i + 1)
  }
  return c
}

function hypergeometric(N, K, n, k) {
  if (k < 0 || k > Math.min(K, n)) return 0
  if (k > n || k > K) return 0
  const p = (combinations(K, k) * combinations(N - K, n - k)) / combinations(N, n)
  return p
}

// 计算累积概率 P(X >= target)
function calcOdds(N, K, n, target) {
  let total = 0
  for (let k = target; k <= Math.min(K, n); k++) {
    total += hypergeometric(N, K, n, k)
  }
  return total
}

// 赛制预设
const FORMAT_PRESETS = {
  '标准/摩登/特选': { deckSize: 60, life: 20, hand: 7 },
  '先驱': { deckSize: 60, life: 20, hand: 7 },
  '薪传': { deckSize: 60, life: 20, hand: 7 },
  '指挥官 1v1': { deckSize: 59, life: 20, hand: 7 },
  '指挥官 (4人)': { deckSize: 99, life: 40, hand: 7 }
}

Page({
  data: {
    isLightTheme: false,

    // 赛制
    formatNames: Object.keys(FORMAT_PRESETS),
    selectedFormat: '标准/摩登/特选',

    // 套牌
    deckSize: 60,
    handSize: 7,
    totalCards: 60,

    // 目标牌
    targetCount: 4,
    targetName: '',
    targetDraws: [],

    // 计算结果
    odds: {
      opening: {},
      cumulative: {}
    },
    oddsPct: {},
    oddsCumPct: {},
    oddsCumHigh: {},

    // 已选套牌
    selectedDeck: null
  },

  onLoad(query) {
    this.setData({ isLightTheme: app.globalData.isLightTheme })

    // 接收传入的套牌
    if (query.deck) {
      try {
        const deck = JSON.parse(decodeURIComponent(query.deck))
        this.applyDeck(deck)
      } catch (e) {
        console.error('Failed to parse deck', e)
      }
    }
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  updateTheme(isLight) {
    this.setData({ isLightTheme: isLight })
  },

  // 应用套牌到计算器
  applyDeck(deck) {
    const deckSize = deck.totalCards || 60
    const format = deck.format || '标准'
    let preset = FORMAT_PRESETS['标准/摩登/特选']
    if (format === '指挥官') {
      preset = FORMAT_PRESETS['指挥官 (4人)']
    }

    // 找最常见的牌的种类作为目标
    const topCard = deck.cards && deck.cards.length > 0 ? deck.cards[0] : null
    const targetCount = topCard ? topCard.count : 4

    this.setData({
      selectedDeck: deck,
      deckSize: deckSize,
      totalCards: deckSize,
      targetCount: targetCount,
      targetName: topCard ? topCard.name : '',
      selectedFormat: format
    })

    this.calculate()
  },

  // 选择赛制
  selectFormat(e) {
    const index = parseInt(e.detail.value)
    const name = this.data.formatNames[index]
    const preset = FORMAT_PRESETS[name]
    this.setData({
      selectedFormat: name,
      deckSize: preset.deckSize,
      handSize: preset.hand
    })
    this.calculate()
  },

  // 设置套牌总张数
  setDeckSize(e) {
    const size = parseInt(e.detail.value) || 60
    this.setData({ deckSize: size, totalCards: size })
    this.calculate()
  },

  // 设置目标牌数量
  setTargetCount(e) {
    const count = parseInt(e.detail.value) || 4
    this.setData({ targetCount: count })
    this.calculate()
  },

  // 设置目标牌名称
  setTargetName(e) {
    this.setData({ targetName: e.detail.value })
  },

  // 计算概率
  calculate() {
    const { deckSize, targetCount, handSize } = this.data
    const N = deckSize
    const K = targetCount
    const n = handSize

    const odds = { opening: {}, cumulative: {} }

    for (let k = 0; k <= Math.min(K, n); k++) {
      const p = hypergeometric(N, K, n, k)
      odds.opening[k] = p
      if (k === 0) odds.cumulative[k] = p
    }

    // 累积概率 P(X >= k)
    for (let k = 1; k <= Math.min(K, n); k++) {
      odds.cumulative[k] = calcOdds(N, K, n, k)
    }

    // 预计算百分比字符串
    const pct = {}
    for (const k in odds.opening) {
      pct[k] = (odds.opening[k] * 100).toFixed(1)
    }
    const cumPct = {}
    const cumHigh = {}
    for (const k in odds.cumulative) {
      cumPct[k] = (odds.cumulative[k] * 100).toFixed(1)
      cumHigh[k] = odds.cumulative[k] > 0.5
    }

    // 计算各回合抽到张数期望
    const draws = []
    for (let turn = 1; turn <= 7; turn++) {
      const hand = turn === 1 ? 7 : 7 + turn - 1
      const p = hypergeometric(N, K, hand, 1)
      draws.push({ turn, pct: (p * 100).toFixed(0), barWidth: (p * 100).toFixed(1) })
    }

    this.setData({
      odds,
      oddsPct: pct,
      oddsCumPct: cumPct,
      oddsCumHigh: cumHigh,
      targetDraws: draws
    })
  },

  // 从套牌列表选择
  pickDeck() {
    const decks = wx.getStorageSync('mtg_decks') || []
    if (decks.length === 0) {
      wx.showToast({ title: '暂无套牌', icon: 'none' })
      return
    }

    wx.showActionSheet({
      itemList: decks.map(d => `${d.name} (${d.totalCards}张)`),
      success: (res) => {
        this.applyDeck(decks[res.tapIndex])
      }
    })
  },

  // 跳转到套牌列表
  goToDecks() {
    wx.navigateTo({ url: '/pages/decks/decks' })
  },

  goToIndex() {
    wx.redirectTo({ url: '/pages/index/index' })
  }
})