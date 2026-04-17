// pages/deck-detail/deck-detail.js
const app = getApp()

Page({
  data: {
    isLightTheme: false,
    deck: null,
    deckStr: '',
    // 过滤后的主牌（去除指挥官）
    mainCards: [],
    // 指挥官信息
    commanderInfo: null,
    // 按类型分类的卡牌
    creatureCards: [],
    sorceryCards: [],
    instantCards: [],
    planeswalkerCards: [],
    enchantmentCards: [],
    artifactCards: [],
    landCards: [],
    otherCards: []
  },

  onLoad(query) {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    if (query.deck) {
      try {
        const deck = JSON.parse(decodeURIComponent(query.deck))
        const { mainCards, commanderInfo } = this.processDeck(deck)
        this.setData({ deck, deckStr: query.deck, mainCards, commanderInfo })
        if (commanderInfo) {
          this.fetchCommanderImage(commanderInfo.name)
        }
        // 批量获取卡牌类型
        if (mainCards.length > 0) {
          this.fetchCardTypes(mainCards)
        }
      } catch (e) {
        console.error('Failed to parse deck', e)
      }
    }
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 处理套牌数据，分离主牌和指挥官
  processDeck(deck) {
    let commanderInfo = null
    if (deck.commander && deck.format === '指挥官') {
      // 从卡牌列表中移除指挥官
      const mainCards = deck.cards.filter(c => c.name !== deck.commander)
      commanderInfo = { name: deck.commander, image: '' }
      return { mainCards, commanderInfo }
    }
    return { mainCards: deck.cards, commanderInfo: null }
  },

  // 获取指挥官图片
  fetchCommanderImage(name) {
    wx.request({
      url: 'https://api.scryfall.com/cards/named',
      data: { fuzzy: name },
      timeout: 10000,
      success: (res) => {
        if (res.data && res.data.image_uris) {
          this.setData({
            commanderInfo: {
              name: res.data.name,
              image: res.data.image_uris.small || res.data.image_uris.normal,
              type_line: res.data.type_line || ''
            }
          })
        }
      }
    })
  },

  // 规范化卡名 key（统一大小写、去除多余空格、统一斜杠格式）
  normalizeKey(name) {
    if (!name) return ''
    // 统一斜杠格式：去除斜杠周围空格，转换单斜杠为双斜杠
    let normalized = name.toLowerCase()
    normalized = normalized.replace(/\s*\/\s*/g, ' // ')  // 单斜杠变双斜杠
    normalized = normalized.replace(/\s+/g, ' ').trim()   // 去除多余空格
    return normalized
  },

  // 批量获取卡牌类型用于分类
  fetchCardTypes(cards) {
    const identifiers = cards.map(c => ({ name: c.name }))
    const chunkSize = 75
    const allTypes = {}
    const self = this

    const processChunk = (index) => {
      if (index >= identifiers.length) {
        self.categorizeCards(cards, allTypes)
        return
      }
      const chunk = identifiers.slice(index, index + chunkSize)
      wx.request({
        url: 'https://api.scryfall.com/cards/collection',
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        data: JSON.stringify({ identifiers: chunk }),
        timeout: 30000,
        success: (res) => {
          if (res.data && res.data.data) {
            for (const card of res.data.data) {
              // 双面牌取正面 (card_faces[0]) 的类型和法力费用
              let typeLine = card.type_line || ''
              let manaCost = card.mana_cost || ''
              let frontName = card.name || ''
              if (card.card_faces && card.card_faces.length > 0) {
                typeLine = card.card_faces[0].type_line || typeLine
                manaCost = card.card_faces[0].mana_cost || manaCost
                frontName = card.card_faces[0].name || frontName
              }
              const primaryType = self.getPrimaryType(typeLine)
              const cardInfo = { type_line: typeLine, primaryType, mana_cost: manaCost }

              // 同时用 Scryfall 返回的卡名（正面）和原始卡名做 key，确保都能查到
              const cardNameKey = self.normalizeKey(card.name)
              const frontNameKey = self.normalizeKey(frontName)
              allTypes[cardNameKey] = cardInfo
              if (frontNameKey !== cardNameKey) {
                allTypes[frontNameKey] = cardInfo
              }
            }
          }
          processChunk(index + chunkSize)
        },
        fail: () => {
          processChunk(index + chunkSize)
        }
      })
    }

    processChunk(0)
  },

  // 获取主要类型
  getPrimaryType(typeLine) {
    if (!typeLine) return 'other'
    const typeLineLower = typeLine.toLowerCase()
    if (typeLineLower.includes('creature')) return 'creature'
    if (typeLineLower.includes('planeswalker')) return 'planeswalker'
    if (typeLineLower.includes('instant')) return 'instant'
    if (typeLineLower.includes('sorcery')) return 'sorcery'
    if (typeLineLower.includes('enchantment')) return 'enchantment'
    if (typeLineLower.includes('artifact')) return 'artifact'
    if (typeLineLower.includes('land')) return 'land'
    return 'other'
  },

  // 获取法力费用符号图片
  getManaSymbols(manaCost) {
    if (!manaCost) return []
    const symbols = manaCost.match(/\{([^}]+)\}/g) || []
    return symbols.map(s => {
      const symbol = s.replace(/[{}]/g, '')
      return {
        url: `https://svgs.scryfall.io/card-symbols/${symbol.replace('/', '')}.svg`,
        key: symbol
      }
    })
  },

  // 分类卡牌
  categorizeCards(cards, typeMap) {
    const creatureCards = []
    const sorceryCards = []
    const instantCards = []
    const planeswalkerCards = []
    const enchantmentCards = []
    const artifactCards = []
    const landCards = []
    const otherCards = []

    for (const card of cards) {
      const key = this.normalizeKey(card.name)
      let info = typeMap[key]
      // 候补：如果没找到，尝试去掉 " // xxx" 部分（双面牌正面名）
      if (!info) {
        const altKey = key.split(' //')[0].trim()
        if (altKey !== key) {
          info = typeMap[altKey]
        }
      }
      const primaryType = info ? info.primaryType : 'other'
      const manaCost = info ? info.mana_cost : ''
      const manaSymbols = this.getManaSymbols(manaCost)

      const cardData = { ...card, type_line: info ? info.type_line : '', mana_cost: manaCost, manaSymbols }

      switch (primaryType) {
        case 'creature':
          creatureCards.push(cardData)
          break
        case 'sorcery':
          sorceryCards.push(cardData)
          break
        case 'instant':
          instantCards.push(cardData)
          break
        case 'planeswalker':
          planeswalkerCards.push(cardData)
          break
        case 'enchantment':
          enchantmentCards.push(cardData)
          break
        case 'artifact':
          artifactCards.push(cardData)
          break
        case 'land':
          landCards.push(cardData)
          break
        default:
          otherCards.push(cardData)
      }
    }

    this.setData({
      creatureCards,
      sorceryCards,
      instantCards,
      planeswalkerCards,
      enchantmentCards,
      artifactCards,
      landCards,
      otherCards
    })
  },

  goToIndex() {
    wx.redirectTo({ url: '/pages/index/index' })
  },

  // 计算Odds
  goToOdds() {
    const { deckStr } = this.data
    if (!deckStr) return
    wx.navigateTo({
      url: `/pages/odds/odds?deck=${deckStr}`
    })
  },

  // 分享卡组
  shareDeck() {
    const { deck } = this.data
    if (!deck) return

    const text = deck.cards.map(c => `${c.count} ${c.name}`).join('\n')
    const shareText = `【${deck.name}】\n赛制：${deck.format}\n指挥官：${deck.commander || '无'}\n总张数：${deck.totalCards}\n平均法术力费用：${deck.avgCMC}\n\n${text}`

    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    wx.showToast({ title: '已准备分享', icon: 'none' })
  },

  // 复制导出
  exportDeck() {
    const { deck } = this.data
    if (!deck) return

    const text = deck.cards.map(c => `${c.count} ${c.name}`).join('\n')
    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' })
      }
    })
  }
})
