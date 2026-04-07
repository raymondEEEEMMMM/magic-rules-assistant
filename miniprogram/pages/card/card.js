// pages/card/card.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    keyword: '',
    cards: [],
    filteredCards: [],
    loading: false,
    searchDone: false,
    showDetail: false,
    currentCard: null,
    useApi: true,  // 默认使用API模式
    isLightTheme: true,
    // 分页
    page: 1,
    pageSize: 20,
    hasMore: false,
    loadingMore: false,
    totalCards: 0,
    // 视图模式
    viewMode: 'image', // 'image' or 'text'
    // 筛选
    showFilter: false,
    filterColor: [],
    filterCmc: '',
    filterType: '',
    filterRarity: ''
  },

  onLoad(options) {
    console.log('CODEBUDDY_DEBUG card onLoad options=', options)
    this.setData({ isLightTheme: true })
    // 如果有 id 参数
    if (options.id) {
      const id = decodeURIComponent(options.id)
      this.setData({ keyword: id })
      // 判断是关键词还是卡牌ID（UUID格式）
      if (this._isUUID(id)) {
        // 是 UUID，加载卡牌详情
        console.log('CODEBUDDY_DEBUG card onLoad id is UUID, loading detail')
        this.fetchCardDetail(id)
      } else {
        // 是关键词，执行搜索
        console.log('CODEBUDDY_DEBUG card onLoad id is keyword, performing search')
        this.performApiSearch(id)
      }
    } else {
      console.log('CODEBUDDY_DEBUG card onLoad no id parameter')
    }
    console.log('CODEBUDDY_DEBUG card onLoad completed')
  },

  // 判断是否UUID格式
  _isUUID(str) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    return uuidRegex.test(str)
  },

  onShow() {
    this.setData({ isLightTheme: true })
  },

  // 返回
  goBack() {
    wx.navigateBack({
      fail: () => {
        wx.switchTab({ url: '/pages/index/index' })
      }
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
      showDetail: false,
      page: 1,
      hasMore: false,
      totalCards: 0
    })

    this.performApiSearch(keyword)
  },

  // 加载更多
  loadMore() {
    if (this.data.loadingMore || !this.data.hasMore) return
    this.setData({
      loadingMore: true,
      page: this.data.page + 1
    })
    this.performApiSearch(this.data.keyword, true)
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
  performApiSearch(keyword, append = false) {
    const { page, pageSize } = this.data
    api.searchCard(keyword, page, pageSize).then(res => {
      if (res && res.items) {
        const cards = res.items.map(item => ({
          id: item.id,
          name: item.zhs_name || item.name,
          manaCost: item.mana_cost || '',
          type: item.zhs_type_line || item.type_line || '',
          text: item.oracle_text || '',
          power: item.power || '',
          toughness: item.toughness || '',
          setName: item.zhs_set_name || item.set_name || '',
          collectorNumber: item.collector_number || '',
          rarity: item.rarity || '',
          colors: item.colors || [],
          cmc: item.cmc || 0,
          imageUrl: item.zhs_image_uris?.normal || item.image_uris?.normal || ''
        }))

        const totalPages = res.total_pages || 1
        const hasMore = page < totalPages

        const newCards = append ? this.data.cards.concat(cards) : cards

        this.setData({
          loading: false,
          loadingMore: false,
          searchDone: true,
          cards: newCards,
          filteredCards: newCards,
          hasMore,
          totalCards: res.count || cards.length
        })

        // 重置筛选
        this.resetFilters()

        if (cards.length === 0 && !append) {
          wx.showToast({
            title: '未找到相关卡牌',
            icon: 'none'
          })
        }
      } else {
        this.setData({
          loading: false,
          loadingMore: false,
          searchDone: true,
          cards: [],
          filteredCards: [],
          hasMore: false
        })
      }
    }).catch(err => {
      console.error('卡牌搜索失败:', err)
      this.setData({
        loading: false,
        loadingMore: false,
        searchDone: true,
        cards: [],
        filteredCards: [],
        hasMore: false
      })
      wx.showToast({
        title: '搜索失败',
        icon: 'none'
      })
    })
  },

  // 切换筛选器显示
  toggleFilter() {
    this.setData({ showFilter: !this.data.showFilter })
  },

  // 重置筛选
  resetFilters() {
    this.setData({
      filterColor: [],
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

  // 颜色筛选（多选）
  onColorFilter(e) {
    const color = e.currentTarget.dataset.color
    let current = this.data.filterColor || []
    if (!Array.isArray(current)) current = []

    const index = current.indexOf(color)
    if (index > -1) {
      current.splice(index, 1)
    } else {
      current.push(color)
    }
    this.setData({ filterColor: current })
    this.applyFilters()
  },

  // 类别筛选
  onTypeFilter(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ filterType: this.data.filterType === type ? '' : type })
    this.applyFilters()
  },

  // 应用筛选
  applyFilters() {
    const { cards, filterColor, filterType, filterCmc, filterRarity } = this.data
    let filtered = cards

    if (filterColor && filterColor.length > 0) {
      filtered = filtered.filter(card => card.colors && filterColor.some(c => card.colors.includes(c)))
    }

    if (filterType) {
      filtered = filtered.filter(card => card.type && card.type.includes(filterType))
    }

    if (filterCmc !== '') {
      if (filterCmc === '6+') {
        filtered = filtered.filter(card => card.cmc >= 6)
      } else {
        filtered = filtered.filter(card => card.cmc == parseFloat(filterCmc))
      }
    }

    if (filterRarity) {
      filtered = filtered.filter(card => card.rarity === filterRarity)
    }

    this.setData({ filteredCards: filtered })
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
        const manaSymbols = this.getManaSymbols(card.mana_cost || '')

        // 处理规则文本（转换 \\n 为真正换行）
        const oracleText = this.convertNewlines(card.zhs_text || card.oracle_text || '')
        const enText = this.convertNewlines(card.oracle_text || '')
        // 解析规则文本中的法力符号
        const textSegments = this.parseOracleText(oracleText)
        const enTextSegments = this.parseOracleText(enText)

        this.setData({
          currentCard: {
            id: card.id,
            name: card.zhs_name || card.name,
            enName: card.name,
            manaCost: manaCost,
            manaSymbols: manaSymbols,
            type: card.zhs_type_line || card.type_line || '',
            text: oracleText,
            textSegments: textSegments,
            enText: enText,
            enTextSegments: enTextSegments,
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

  // 解析规则文本，将法力符号转换为图片
  parseOracleText(text) {
    if (!text) return []
    // 按法力符号分割：{R}, {2}{W}, {X}, {W/U} 等
    const parts = text.split(/(\{[^}]+\})/g)
    return parts.map(part => {
      const match = part.match(/^\{(.+)\}$/)
      if (match) {
        const symbol = match[1].replace('/', '')
        return {
          type: 'mana',
          url: `https://svgs.scryfall.io/card-symbols/${symbol}.svg`,
          text: part
        }
      }
      return {
        type: 'text',
        text: part
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
    wx.navigateBack({
      fail: () => {
        wx.switchTab({ url: '/pages/index/index' })
      }
    })
  },

  // 切换视图模式
  toggleView() {
    this.setData({
      viewMode: this.data.viewMode === 'image' ? 'text' : 'image'
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
