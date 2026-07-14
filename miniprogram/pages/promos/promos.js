// pages/promos/promos.js
const app = getApp()

Page({
  data: {
    isLightTheme: true,
    cards: [],
    allCards: [],
    page: 1,
    pageSize: 20,
    hasMore: true,
    loading: false,
    years: [],
    selectedYear: '',
    showYearFilter: false
  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    this.loadYears()
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 加载可选年份
  loadYears() {
    const currentYear = new Date().getFullYear()
    const years = [currentYear.toString(), (currentYear - 1).toString()]
    this.setData({ years, selectedYear: currentYear.toString() })
    this.loadCards()
  },

  // 加载卡片数据
  loadCards() {
    if (this.data.loading) return
    this.setData({ loading: true })

    wx.cloud.callFunction({
      name: 'mtgAsk',
      data: {
        httpMethod: 'GET',
        path: '/api/promos',
        queryString: `year=${this.data.selectedYear}`
      },
      success: (res) => {
        if (res.result && res.result.body) {
          const data = typeof res.result.body === 'string' ? JSON.parse(res.result.body) : res.result.body
          if (data.success && data.cards) {
            // 按发布时间降序排序
            const sortedCards = data.cards.sort((a, b) => {
              return new Date(b.released_at) - new Date(a.released_at)
            })
            this.setData({
              allCards: sortedCards,
              cards: sortedCards.slice(0, this.data.pageSize),
              hasMore: sortedCards.length > this.data.pageSize,
              page: 1
            })
          }
        }
        this.setData({ loading: false })
      },
      fail: (err) => {
        console.error('获取 Promo 卡失败:', err)
        this.setData({ loading: false })
      }
    })
  },

  // 加载更多
  loadMore() {
    if (this.data.loading || !this.data.hasMore) return

    const nextPage = this.data.page + 1
    const end = nextPage * this.data.pageSize
    const newCards = this.data.allCards.slice(0, end)

    this.setData({
      cards: newCards,
      page: nextPage,
      hasMore: end < this.data.allCards.length
    })
  },

  // 选择年份
  onYearChange(e) {
    const index = parseInt(e.detail.value)
    const year = this.data.years[index]
    this.setData({ selectedYear: year })
    this.loadCards()
  },

  // 切换年份筛选显示
  toggleYearFilter() {
    this.setData({ showYearFilter: !this.data.showYearFilter })
  },

  // 返回
  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  // 主题切换
  updateTheme(isLight) {
    this.setData({ isLightTheme: isLight })
  },

  // 点击 promo 卡（已有逻辑：传递到 card 详情）
  onPromoTap(e) {
    const promo = e.currentTarget.dataset.promo
    if (!promo) return

    // 将卡牌数据通过本地存储传递（避免 URL 参数长度限制）
    try {
      wx.setStorageSync('promoCardData', promo)
    } catch (e) {
      console.error('存储卡牌数据失败:', e)
    }

    const url = `/pages/card/card?from=promo`
    wx.navigateTo({ url })
  }
})
