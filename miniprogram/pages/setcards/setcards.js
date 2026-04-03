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
    filteredCards: [],
    loading: false,
    loaded: false,
    viewMode: 'image', // 'image' or 'text'
    isLightTheme: true,
    showFilter: false,  // 筛选器默认收起
    // 筛选条件
    filterColor: '',     // W/U/B/R/G
    filterCmc: '',       // 0-6+
    filterType: '',      // 生物、神器、法术、地、结界
    filterRarity: '',    // c/u/r/m
  },

  onLoad(options) {
    this.setData({ isLightTheme: true })
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

  // 返回
  goBack() {
    console.log('CODEBUDDY_DEBUG setcards goBack called')
    wx.navigateBack({
      success: () => console.log('CODEBUDDY_DEBUG setcards goBack success'),
      fail: (err) => {
        console.log('CODEBUDDY_DEBUG setcards goBack fail err=', err)
        wx.switchTab({ url: '/pages/index/index' })
      }
    })
  },

  // 加载系列数据
  loadSetData() {
    const { setCode, setName } = this.data
    this.setData({ loading: true })

    api.getSetCards(setCode, 1, 9999).then(res => {
      console.log('CODEBUDDY_DEBUG API returned, first 3 cards:', JSON.stringify(res.items?.slice(0, 3)))
      const cards = (res.items || []).map(card => ({
        id: card.id,
        display_name: card.display_name || card.name || '',
        image_url: card.image_url || '',
        colors: card.colors || [],
        cmc: card.cmc || 0,
        type_line: card.type_line || '',
        rarity: card.rarity || '',
        mana_cost: card.mana_cost || ''
      }))

      this.setData({
        cards,
        filteredCards: cards,
        setInfo: {
          name: setName,
          code: setCode,
          iconUrl: `https://svgs.scryfall.io/sets/${setCode.toLowerCase()}.svg`
        },
        loading: false,
        loaded: true
      })
    }).catch(err => {
      console.error('CODEBUDDY_DEBUG setcards loadSetData error', err)
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

  // 切换视图模式
  toggleView() {
    this.setData({
      viewMode: this.data.viewMode === 'image' ? 'text' : 'image'
    })
  },

  // 颜色筛选
  onColorFilter(e) {
    const color = e.currentTarget.dataset.color
    const current = this.data.filterColor
    this.setData({ filterColor: current === color ? '' : color })
    this.applyFilters()
  },

  // 切换筛选器显示
  toggleFilter() {
    this.setData({ showFilter: !this.data.showFilter })
  },

  // 重置筛选
  resetFilters() {
    this.setData({
      filterColor: '',
      filterCmc: '',
      filterType: '',
      filterRarity: ''
    })
    this.applyFilters()
  },

  // 法力值筛选
  onCmcFilter(e) {
    const cmc = e.currentTarget.dataset.cmc
    this.setData({ filterCmc: this.data.filterCmc === cmc ? '' : cmc })
    this.applyFilters()
  },

  // 稀有度筛选
  onRarityFilter(e) {
    const rarity = e.currentTarget.dataset.rarity
    this.setData({ filterRarity: this.data.filterRarity === rarity ? '' : rarity })
    this.applyFilters()
  },

  // 类别筛选
  onTypeFilter(e) {
    const type = e.currentTarget.dataset.type
    console.log('CODEBUDDY_DEBUG type filter:', type, 'current:', this.data.filterType)
    this.setData({ filterType: this.data.filterType === type ? '' : type })
    this.applyFilters()
    console.log('CODEBUDDY_DEBUG after filter, filteredCards count:', this.data.filteredCards.length)
  },

  // 应用所有筛选
  applyFilters() {
    const { cards, filterColor, filterCmc, filterType, filterRarity } = this.data
    let filtered = cards
    console.log('CODEBUDDY_DEBUG applyFilters:', { filterColor, filterCmc, filterType, filterRarity, total: cards.length })

    // 按颜色筛选
    if (filterColor) {
      filtered = filtered.filter(card => card.colors && card.colors.includes(filterColor))
    }

    // 按法力值筛选
    if (filterCmc !== '') {
      if (filterCmc === '6+') {
        filtered = filtered.filter(card => card.cmc >= 6)
      } else {
        const targetCmc = parseFloat(filterCmc)
        filtered = filtered.filter(card => card.cmc == targetCmc)
      }
    }

    // 按类别筛选
    if (filterType) {
      filtered = filtered.filter(card => card.type_line && card.type_line.includes(filterType))
    }

    // 按稀有度筛选
    if (filterRarity) {
      filtered = filtered.filter(card => card.rarity === filterRarity)
    }

    console.log('CODEBUDDY_DEBUG filtered result:', filtered.length, 'cards')
    this.setData({ filteredCards: filtered })
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    if (!cardId) return
    const url = `/pages/card/card?id=${encodeURIComponent(cardId)}`
    wx.navigateTo({ url })
  }
})
