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
    error: null,
    useApi: true,  // 默认使用API模式
    isLightTheme: true
  },

  onLoad(options) {
    this.setData({ isLightTheme: true })

    // 如果来自 promo 页面，从本地存储读取卡牌数据
    if (options.from === 'promo') {
      try {
        const promoCard = wx.getStorageSync('promoCardData')
        if (promoCard && promoCard.name) {
          this.setData({
            currentCard: this.formatPromoCard(promoCard),
            showDetail: true,
            loading: false,
            error: null
          })
          wx.removeStorageSync('promoCardData')
          return
        }
      } catch (e) {
        console.error('读取 promo 卡牌数据失败:', e)
      }
    }

    // 如果有 id 参数，直接加载卡牌详情
    if (options.id) {
      this.setData({ keyword: decodeURIComponent(options.id) })
      this.fetchCardDetail(options.id)
    } else {
    }
  },

  onShow() {
    this.setData({ isLightTheme: true })
  },

  // 返回
  goToIndex() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
  },

  // 返回上一页（带 fallback）
  goBack() {
    wx.navigateBack({
      fail: () => wx.redirectTo({ url: '/pages/index/index' })
    })
  },

  // 重试
  onRetry() {
    this.setData({ error: null })
    const keyword = this.data.keyword
    if (keyword) this.performApiSearch(keyword)
  },

  // 分享提示
  onShare() {
    wx.showToast({ title: '点击右上角分享', icon: 'none' })
  },

  // 复制牌名
  onCopyName() {
    const card = this.data.currentCard
    const name = card && (card.zhs_name || card.name)
    if (name) {
      wx.setClipboardData({
        data: name,
        success: () => wx.showToast({ title: '已复制', icon: 'success' })
      })
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
    this.setData({ loading: true, error: null })

    api.getCardById(cardId).then(card => {
      wx.hideLoading()

      if (card && card.name) {
        // 处理关键词异能
        const keywords = card.keywords || []

        // 处理法力费用显示
        const manaCost = this.formatManaCost(card.mana_cost || '')
        const manaSymbols = this.getManaSymbols(card.mana_cost || '')

        // 处理规则文本（转换 \\n 为真正换行）
        const oracleText = this.convertNewlines(card.zhs_text || card.oracle_text || '')
        const enText = this.convertNewlines(card.oracle_text || '')

        this.setData({
          currentCard: {
            id: card.id,
            name: card.name,
            zhs_name: card.zhs_name || card.name,
            enName: card.name,
            manaCost: manaCost,
            manaSymbols: manaSymbols,
            mana_cost: card.mana_cost || '',
            type: card.zhs_type_line || card.type_line || '',
            type_line: card.zhs_type_line || card.type_line || '',
            text: oracleText,
            enText: enText,
            oracle_text: oracleText,
            flavor_text: card.flavor_text || '',
            power: card.power !== undefined && card.power !== null ? card.power : '',
            toughness: card.toughness !== undefined && card.toughness !== null ? card.toughness : '',
            setName: card.zhs_set_name || card.set_name || '',
            collectorNumber: card.collector_number || '',
            rarity: card.rarity || '',
            imageUrl: card.zhs_image_uris?.normal || card.image_uris?.normal || '',
            image_uris: card.image_uris || {},
            keywords: keywords,
            legalities: card.legalities || {},
            rulings: []
          },
          loading: false,
          error: null,
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
      this.setData({
        loading: false,
        error: (err && (err.errMsg || err.message)) || '网络错误，请稍后重试'
      })
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

  // 格式化 Promo 卡牌数据
  formatPromoCard(card) {
    const oracleText = this.convertNewlines(card.oracle_text || '')
    const manaCost = card.mana_cost || ''
    const manaSymbols = this.getManaSymbols(manaCost)
    const imageUrl = card.image_url || ''
    return {
      id: card.id || '',
      name: card.name || '',
      display_name: card.name || '',
      zhs_name: card.name || '',
      imageUrl: imageUrl,
      image_uris: imageUrl ? { normal: imageUrl } : {},
      type: card.type_line || '',
      type_line: card.type_line || '',
      mana_cost: manaCost,
      manaCost: manaCost,
      text: oracleText,
      enText: oracleText,
      oracle_text: oracleText,
      flavor_text: card.flavor_text || '',
      manaSymbols: manaSymbols,
      colors: card.colors || [],
      rarity: card.rarity || '',
      power: card.power !== undefined && card.power !== null ? card.power : '',
      toughness: card.toughness !== undefined && card.toughness !== null ? card.toughness : '',
      setName: card.set_name || '',
      set_name: card.set_name || '',
      released_at: card.released_at || '',
      acquisition_method: card.acquisition_method || '',
      acquisition_method_cn: card.acquisition_method_cn || card.acquisition_method || '',
      security_stamp: card.security_stamp || ''
    }
  },

  // 格式化法力费用（转换为纯文本）
  formatManaCost(manaCost) {
    if (!manaCost) return ''
    return manaCost.replace(/\{([^}]+)\}/g, '$1')
  },

  // 获取法力费用符号图片
  getManaSymbols(manaCost) {
    if (!manaCost) return []
    const symbols = manaCost.match(/\{([^}]+)\}/g) || []
    return symbols.map(s => {
      const symbol = s.replace(/[{}]/g, '')
      // 处理混合法力费用如 W/U -> WU
      const symbolKey = symbol.replace('/', '')
      return {
        url: `https://svgs.scryfall.io/card-symbols/${symbol.replace('/', '')}.svg`,
        key: symbol
      }
    })
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
  },

  // 复制卡牌名称
  copyCardName(e) {
    const cardName = e.currentTarget.dataset.name || this.data.currentCard.name
    wx.setClipboardData({
      data: cardName,
      success: () => {
        wx.showToast({
          title: '已复制: ' + cardName,
          icon: 'none',
          duration: 2000
        })
      },
      fail: () => {
        wx.showToast({
          title: '复制失败',
          icon: 'none'
        })
      }
    })
  }
})
