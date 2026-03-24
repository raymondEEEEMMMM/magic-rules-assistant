// pages/card/card.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    keyword: '',
    cards: [],
    loading: false,
    searchDone: false,
    showDetail: false,
    currentCard: null,
    useApi: true,  // 默认使用API模式
    isLightTheme: true
  },

  onLoad(options) {
    this.setData({ isLightTheme: true })
    // 如果有 id 参数，直接加载卡牌详情
    if (options.id) {
      this.setData({ keyword: decodeURIComponent(options.id) })
      this.fetchCardDetail(options.id)
    }
  },

  onShow() {
    this.setData({ isLightTheme: true })
  },

  // 返回
  goBack() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
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
    api.searchCard(keyword, 1, 10).then(res => {
      if (res && res.items) {
        const cards = res.items.map(item => ({
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
    }).catch(err => {
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

    api.getCardById(cardId).then(card => {
      wx.hideLoading()

      if (card && card.name) {
        // 处理关键词异能
        const keywords = card.keywords || []

        // 处理法力费用显示
        const manaCost = this.formatManaCost(card.mana_cost || '')

        // 处理规则文本（转换 \\n 为真正换行）
        const oracleText = this.convertNewlines(card.zhs_text || card.oracle_text || '')
        const enText = this.convertNewlines(card.oracle_text || '')

        this.setData({
          currentCard: {
            id: card.id,
            name: card.zhs_name || card.name,
            enName: card.name,
            manaCost: manaCost,
            type: card.zhs_type_line || card.type_line || '',
            text: oracleText,
            enText: enText,
            power: card.power || '',
            toughness: card.toughness || '',
            setName: card.zhs_set_name || card.set_name || '',
            collectorNumber: card.collector_number || '',
            rarity: card.rarity || '',
            imageUrl: card.zhs_image_uris?.normal || card.image_uris?.normal || '',
            keywords: keywords,
            legalities: card.legalities || {},
            rulings: []
          },
          showDetail: true
        })

        // 获取官方裁定（MTGCH id 就是 Scryfall card ID）
        if (card.id) {
          this.fetchCardRulings(card.id)
        }
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('卡牌详情加载失败:', err)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  // 转换 \\n 为真正换行符
  convertNewlines(text) {
    if (!text) return ''
    return text.replace(/\\n/g, '\n')
  },

  // 格式化法力费用
  formatManaCost(manaCost) {
    if (!manaCost) return ''
    // 将 {2}{B} 转换为 2B 格式
    return manaCost.replace(/\{([^}]+)\}/g, '$1')
  },

  // 获取卡牌官方裁定
  fetchCardRulings(cardId) {
    api.getCardRulings(cardId).then(rulings => {
      this.setData({
        'currentCard.rulings': rulings
      })
    }).catch(err => {
      console.log('裁定获取失败', err)
    })
  },

  closeDetail() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
  },

  // 图片加载失败
  onImageError(e) {
    console.log('图片加载失败', e)
    if (this.data.currentCard) {
      this.setData({
        'currentCard.imageUrl': 'https://via.placeholder.com/200x280/1a1a2e/e94560?text=' + (this.data.currentCard.name || 'No Image')
      })
    }
  },

  // 阻止弹窗关闭
  preventClose(e) {
    // 空函数，阻止事件冒泡
  }
})
