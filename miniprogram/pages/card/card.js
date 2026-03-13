// pages/card/card.js
const app = getApp()

Page({
  data: {
    keyword: '',
    cards: [],
    loading: false,
    searchDone: false,
    showDetail: false,
    currentCard: null
  },

  onLoad(options) {
    // 如果有传入卡牌数据
    if (options.card) {
      try {
        const card = JSON.parse(decodeURIComponent(options.card))
        this.setData({
          currentCard: card,
          showDetail: true
        })
      } catch (e) {
        console.error('解析卡牌数据失败', e)
      }
    }
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.setData({ 
      loading: true,
      searchDone: false 
    })

    app.requestApi('/api/card', { 
      q: keyword,
      page_size: 20
    })
      .then(res => {
        this.setData({
          loading: false,
          searchDone: true,
          cards: res.items || []
        })
      })
      .catch(err => {
        this.setData({
          loading: false,
          searchDone: true
        })
        wx.showToast({
          title: '搜索失败',
          icon: 'none'
        })
      })
  },

  showCardDetail(e) {
    const card = e.currentTarget.dataset.card
    this.setData({
      currentCard: card,
      showDetail: true
    })
  },

  closeDetail() {
    this.setData({
      showDetail: false
    })
  },

  preventClose() {
    // 阻止关闭
  }
})
