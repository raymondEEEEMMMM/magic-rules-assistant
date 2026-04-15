// pages/token/token.js
const app = getApp()

// 中英对照表
const cnToEnMap = {
  '珍宝': 'Treasure',
  '士兵': 'Soldier',
  '天使': 'Angel',
  '精灵': 'Elf',
  '野狼': 'Wolf',
  '猫': 'Cat',
  '鸟': 'Bird',
  '海洋幻惑': 'Kraken',
  '元素': 'Elemental',
  '虚影': 'Spirit',
  '灵俑': 'Zombie',
  '吸血鬼': 'Vampire',
  '蝙蝠': 'Bat',
  '恶魔': 'Demon',
  '妖精': 'Fae',
  '龙': 'Dragon',
  '鬼怪': 'Goblin',
  '龙兽': 'Drake',
  '巨魔': 'Troll',
  '蜈蚣': 'Squirrel',
  '精怪': 'Shapeshifter',
  '组构体': 'Construct',
  '皮托斯': 'Myr',
  '武士': 'Samurai',
  '狼': 'Wolf',
  '老虎': 'Cat',
  '蜜蜂': 'Insect',
  '蝴蝶': 'Butterfly',
  '蛇': 'Snake',
  '螃蟹': 'Crab',
  '蛤蟆': 'Frog',
  '豹': 'Cat',
  '大象': 'Elephant',
  '老鹰': 'Bird',
  '老虎': 'Cat',
  '犀牛': 'Rhino',
  '海龟': 'Turtle',
  '骷髅': 'Skeleton',
  '木乃伊': 'Mummy',
  '食人魔': 'Ogre',
  '巨人': 'Giant',
  '战士': 'Warrior',
  '祭师': 'Cleric',
  '法师': 'Wizard',
  '游侠': 'Ranger',
  '浪人': 'Rogue'
}

// 翻译为英文（优先从映射表查，查不到返回原值）
function translateToEn(cn) {
  return cnToEnMap[cn] || cn
}

Page({
  data: {
    isLightTheme: false,
    searchQuery: '',
    searchResults: [],
    isSearching: false,
    showSearchResults: false,
    tokens: [
      // Treasure (首位)
      { name: '珍宝', enName: 'Treasure', color: 'C', icon: '💎', colorName: '无色' },

      // White
      { name: '士兵', enName: 'Soldier', color: 'W', power: 1, toughness: 1, icon: '⚔️', colorName: '白' },
      { name: '天使', enName: 'Angel', color: 'W', power: 3, toughness: 3, icon: '👼', colorName: '白', abilities: '飞行' },
      { name: '精灵', enName: 'Elf', color: 'W', power: 1, toughness: 1, icon: '🧝', colorName: '白', abilities: '飞行' },
      { name: '野狼', enName: 'Wolf', color: 'W', power: 2, toughness: 2, icon: '🐺', colorName: '白' },
      { name: '猫', enName: 'Cat', color: 'W', power: 2, toughness: 2, icon: '🐱', colorName: '白' },

      // Blue
      { name: '鸟', enName: 'Bird', color: 'U', power: 1, toughness: 1, icon: '🐦', colorName: '蓝', abilities: '飞行' },
      { name: '海洋幻惑', enName: 'Kraken', color: 'U', power: 0, toughness: 0, icon: '🦑', colorName: '蓝' },
      { name: '元素', enName: 'Elemental', color: 'U', power: 0, toughness: 0, icon: '🌊', colorName: '蓝' },
      { name: '虚影', enName: 'Spirit', color: 'U', power: 2, toughness: 2, icon: '👤', colorName: '蓝', abilities: '飞行' },

      // Black
      { name: '灵俑', enName: 'Zombie', color: 'B', power: 2, toughness: 2, icon: '💀', colorName: '黑' },
      { name: '吸血鬼', enName: 'Vampire', color: 'B', power: 1, toughness: 1, icon: '🧛', colorName: '黑' },
      { name: '蝙蝠', enName: 'Bat', color: 'B', power: 1, toughness: 1, icon: '🦇', colorName: '黑', abilities: '飞行' },
      { name: '恶魔', enName: 'Demon', color: 'B', power: 5, toughness: 5, icon: '😈', colorName: '黑', abilities: '飞行' },
      { name: '妖精', enName: 'Fae', color: 'B', power: 0, toughness: 1, icon: '🧚', colorName: '黑' },

      // Red
      { name: '龙', enName: 'Dragon', color: 'R', power: 2, toughness: 2, icon: '🐉', colorName: '红', abilities: '飞行' },
      { name: '鬼怪', enName: 'Goblin', color: 'R', power: 1, toughness: 1, icon: '👺', colorName: '红' },
      { name: '元素', enName: 'Elemental', color: 'R', power: 1, toughness: 1, icon: '🔥', colorName: '红' },
      { name: '龙兽', enName: 'Drake', color: 'R', power: 2, toughness: 2, icon: '🦅', colorName: '红', abilities: '飞行' },

      // Green
      { name: '妖精', enName: 'Elf', color: 'G', power: 1, toughness: 1, icon: '🧝', colorName: '绿' },
      { name: '狼', enName: 'Wolf', color: 'G', power: 2, toughness: 2, icon: '🐺', colorName: '绿' },
      { name: '巨魔', enName: 'Troll', color: 'G', power: 3, toughness: 3, icon: '🧌', colorName: '绿' },
      { name: '蜈蚣', enName: 'Squirrel', color: 'G', power: 1, toughness: 1, icon: '🐿', colorName: '绿' },
      { name: '猫', enName: 'Cat', color: 'G', power: 2, toughness: 1, icon: '🐱', colorName: '绿' },

      // Multicolor / Other
      { name: '精怪', enName: 'Shapeshifter', color: 'C', power: 3, toughness: 3, icon: '👹', colorName: '无色' },
      { name: '组构体', enName: 'Construct', color: 'C', power: 4, toughness: 4, icon: '🤖', colorName: '无色' },
      { name: '皮托斯', enName: 'Myr', color: 'C', power: 0, toughness: 0, icon: '🗿', colorName: '无色' },
    ],
    selectedToken: null,
    showModal: false,
    allCards: [],
    tokenCards: [],
    availableSets: [],  // [{code, name}, ...]  '全部'用code='all'表示
    selectedSetCode: 'all',
    showSetPicker: false,
    selectedCardIndex: 0,
    isLoadingToken: false
  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  goBack() {
    wx.navigateBack()
  },

  selectToken(e) {
    const { enname, name } = e.currentTarget.dataset
    // 从 tokens 数组中找到完整 token 对象
    const token = this.data.tokens.find(t => t.enName === enname) || { name, enName: enname, color: 'C', icon: '🃏', colorName: '无色' }
    this.setData({
      selectedToken: token,
      showModal: true,
      tokenCards: [],
      selectedCardIndex: 0,
      isLoadingToken: true
    })
    this.searchTokenCards(token)
  },

  // 从 Scryfall 搜索 Token 卡图
  searchTokenCards(token) {
    // 构建立即查询 - 使用 Oracle Text 搜索衍生物类型
    const searchName = translateToEn(token.enName)
    // Scryfall 的 t: 只认标准卡牌类型，不认衍生物类型如 Treasure
    // 改用 o:"creates a ${searchName}" 或 o:"${searchName} token" 搜索
    const q = `o:"${searchName} token" is:token -s:fnm`

    wx.request({
      url: `https://api.scryfall.com/cards/search`,
      data: {
        q: q,
        unique: 'art',
        order: 'released'
      },
      success: res => {
        if (res.statusCode === 404 || !res.data || !res.data.data || res.data.data.length === 0) {
          this.setData({ isLoadingToken: false, tokenCards: [], availableSets: [{ code: 'all', name: '全部' }] })
          wx.showToast({ title: '未找到该 Token，请尝试英文搜索', icon: 'none', duration: 2000 })
          return
        }
        if (res.data && res.data.data && res.data.data.length > 0) {
          // 只保存必要字段，减小数据量
          const allCards = res.data.data.map(card => ({
            name: card.name,
            set: card.set,
            set_name: card.set_name,
            image_uris: card.image_uris,
            power: card.power,
            toughness: card.toughness
          }))
          // 提取唯一系列
          const setMap = {}
          allCards.forEach(card => {
            if (card.set_name && card.set) {
              setMap[card.set] = card.set_name
            }
          })
          const availableSets = [{ code: 'all', name: '全部' }]
          Object.keys(setMap).forEach(code => {
            availableSets.push({ code, name: setMap[code] })
          })

          this.setData({
            allCards: allCards,
            tokenCards: allCards,
            availableSets: availableSets,
            selectedSetCode: 'all',
            selectedCardIndex: 0,
            isLoadingToken: false
          })
        } else {
          this.setData({ isLoadingToken: false, tokenCards: [], availableSets: [{ code: 'all', name: '全部' }] })
          wx.showToast({ title: '未找到卡图', icon: 'none' })
        }
      },
      fail: () => {
        this.setData({ isLoadingToken: false })
        wx.showToast({ title: '网络错误，请稍后重试', icon: 'none' })
      }
    })
  },

  // 选择Token卡图
  selectCard(e) {
    const index = e.currentTarget.dataset.index
    this.setData({ selectedCardIndex: index })
  },

  // 按系列筛选
  selectSet(e) {
    const setCode = e.currentTarget.dataset.code
    const { allCards } = this.data

    let filteredCards = allCards
    if (setCode !== 'all') {
      filteredCards = allCards.filter(card => card.set === setCode)
    }

    this.setData({
      selectedSetCode: setCode,
      tokenCards: filteredCards,
      selectedCardIndex: 0,
      showSetPicker: false
    })
  },

  // 切换系列选择器
  toggleSetPicker() {
    this.setData({ showSetPicker: !this.data.showSetPicker })
  },

  // 切换上一张
  prevCard() {
    const { tokenCards, selectedCardIndex } = this.data
    if (selectedCardIndex > 0) {
      this.setData({ selectedCardIndex: selectedCardIndex - 1 })
    }
  },

  // 切换下一张
  nextCard() {
    const { tokenCards, selectedCardIndex } = this.data
    if (selectedCardIndex < tokenCards.length - 1) {
      this.setData({ selectedCardIndex: selectedCardIndex + 1 })
    }
  },

  closeModal() {
    this.setData({ showModal: false, selectedToken: null, tokenCards: [], allCards: [], availableSets: [], selectedSetCode: 'all', selectedCardIndex: 0, showSetPicker: false })
  },

  copyTokenName() {
    if (!this.data.selectedToken) return
    wx.setClipboardData({
      data: this.data.selectedToken.name,
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' })
      }
    })
  },

  saveToken() {
    const { tokenCards, selectedCardIndex } = this.data
    if (!tokenCards || tokenCards.length === 0) return

    const card = tokenCards[selectedCardIndex]
    if (card && card.image_uris) {
      wx.previewImage({
        urls: [card.image_uris.normal || card.image_uris.small],
        success: () => {
          wx.showToast({ title: '长按保存图片', icon: 'none' })
        }
      })
    }
  },

  // 跳转到 Token 生成页
  goToGenerate() {
    const { tokenCards, selectedCardIndex } = this.data
    if (!tokenCards || tokenCards.length === 0) return

    const card = tokenCards[selectedCardIndex]
    const cardStr = encodeURIComponent(JSON.stringify(card))
    wx.navigateTo({
      url: `/pages/token-generate/token-generate?card=${cardStr}`
    })
  },

  // 搜索 Token
  onTokenSearch(e) {
    const query = e.detail.value.trim()
    this.setData({ searchQuery: query })

    if (!query) {
      this.setData({ showSearchResults: false, searchResults: [] })
      return
    }

    this.setData({ isSearching: true, showSearchResults: true })

    const searchName = translateToEn(query)
    const q = `o:"${searchName} token" is:token -s:fnm`

    wx.request({
      url: `https://api.scryfall.com/cards/search`,
      data: {
        q: q,
        unique: 'art',
        order: 'released'
      },
      success: res => {
        if (res.data && res.data.data) {
          const results = res.data.data.slice(0, 9).map(card => ({
            name: card.name,
            image: card.image_uris ? (card.image_uris.normal || card.image_uris.small) : null,
            setName: card.set_name,
            set: card.set,
            power: card.power,
            toughness: card.toughness
          }))
          this.setData({ searchResults: results, isSearching: false })
        } else {
          this.setData({ searchResults: [], isSearching: false })
        }
      },
      fail: () => {
        this.setData({ isSearching: false })
        wx.showToast({ title: '网络错误', icon: 'none' })
      }
    })
  },

  // 点击搜索结果直接选中
  selectSearchResult(e) {
    const item = e.currentTarget.dataset.item
    const card = {
      name: item.name,
      set: item.set,
      set_name: item.setName,
      image_uris: item.image ? { normal: item.image, small: item.image } : null,
      power: item.power,
      toughness: item.toughness
    }
    const token = this.data.tokens.find(t => t.enName.toLowerCase() === item.name.split(' ')[0].toLowerCase()) || {
      name: item.name,
      enName: item.name,
      color: 'C',
      power: parseInt(item.power) || 0,
      toughness: parseInt(item.toughness) || 0,
      icon: '🃏',
      colorName: '无色'
    }

    this.setData({
      selectedToken: token,
      showModal: true,
      showSearchResults: false,
      tokenCards: [card],
      allCards: [card],
      availableSets: [{ code: card.set, name: card.set_name }],
      selectedSetCode: card.set,
      selectedCardIndex: 0,
      isLoadingToken: false,
      searchQuery: ''
    })
  },

  // 清除搜索
  clearSearch() {
    this.setData({ searchQuery: '', searchResults: [], showSearchResults: false })
  }
})
