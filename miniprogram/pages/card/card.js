// pages/card/card.js
const app = getApp()
const API_BASE = 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com'

Page({
  data: {
    keyword: '',
    cards: [],
    loading: false,
    searchDone: false,
    showDetail: false,
    currentCard: null,
    useApi: true  // 默认使用API模式
  },

  onLoad(options) {
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.setData({
      loading: true,
      searchDone: false,
      cards: [],
      showDetail: false
    })

    this.performApiSearch(keyword)
  },

  // 切换 API/本地模式
  toggleApiMode() {
    this.setData({
      useApi: !this.data.useApi,
      cards: [],
      keyword: '',
      searchDone: false
    })
  },

  // API搜索实现
  performApiSearch(keyword) {
    wx.request({
      url: `${API_BASE}/wechat/api/mtgch/search`,
      data: {
        q: keyword,
        page: 1,
        page_size: 10
      },
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.items) {
          const cards = res.data.items.map(item => ({
            id: item.id,
            name: item.name,
            manaCost: item.mana_cost || '',
            type: item.type_line || '',
            text: item.oracle_text || '',
            power: item.power || '',
            toughness: item.toughness || '',
            setName: item.set_name || '',
            collectorNumber: item.collector_number || '',
            rarity: item.rarity || '',
            imageUrl: item.zhs_image_uris?.normal || item.image_uris?.normal || ''
          }))

          this.setData({
            loading: false,
            searchDone: true,
            cards: cards
          })

          if (cards.length === 0) {
            wx.showToast({
              title: '未找到相关卡牌',
              icon: 'none'
            })
          }
        } else {
          this.setData({
            loading: false,
            searchDone: true,
            cards: []
          })
        }
      },
      fail: (err) => {
        console.error('卡牌搜索失败:', err)
        this.setData({
          loading: false,
          searchDone: true,
          cards: []
        })
        wx.showToast({
          title: '搜索失败',
          icon: 'none'
        })
      }
    })
  },

  showCardDetail(e) {
    const card = e.currentTarget.dataset.card
    if (card.id) {
      this.fetchCardDetail(card.id)
    } else {
      this.setData({
        currentCard: card,
        showDetail: true
      })
    }
  },

  // 获取单张卡牌详情
  fetchCardDetail(cardId) {
    wx.showLoading({ title: '加载中...' })

    wx.request({
      url: `${API_BASE}/wechat/api/mtgch/card`,
      data: { id: cardId },
      method: 'GET',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200 && res.data && res.data.name) {
          const card = res.data
          this.setData({
            currentCard: {
              id: card.id,
              name: card.name,
              manaCost: card.mana_cost || '',
              type: card.type_line || '',
              text: card.oracle_text || '',
              power: card.power || '',
              toughness: card.toughness || '',
              setName: card.set_name || '',
              collectorNumber: card.collector_number || '',
              rarity: card.rarity || '',
              imageUrl: card.zhs_image_uris?.normal || card.image_uris?.normal || ''
            },
            showDetail: true
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('卡牌详情加载失败:', err)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    })
  },

  closeDetail() {
    this.setData({
      showDetail: false
    })
  },

  // 阻止弹窗关闭
  preventClose(e) {
    // 空函数，阻止事件冒泡
  }
})
