// pages/token/token.js
const app = getApp()
const api = require('../../utils/api.js')

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
  '虚影': 'Illusion',
  '灵俑': 'Zombie',
  '吸血鬼': 'Vampire',
  '蝙蝠': 'Bat',
  '恶魔': 'Demon',
  '龙': 'Dragon',
  '鬼怪': 'Goblin',
  '龙兽': 'Drake',
  '巨魔': 'Troll',
  '蜈蚣': 'Squirrel',
  '变形兽': 'Shapeshifter',
  '组构体': 'Construct',
  '武士': 'Samurai',
  '狼': 'Wolf',
  '老虎': 'Tiger',
  '蜜蜂': 'Insect',
  '蝴蝶': 'Butterfly',
  '蛇': 'Snake',
  '螃蟹': 'Crab',
  '蛤蟆': 'Frog',
  '豹': 'Leopard',
  '大象': 'Elephant',
  '老鹰': 'Eagle',
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
  '浪客': 'Rogue',
  '精怪': 'Spirit',
  '鹰': 'Bird',
  '玛莉雷基': 'Marit Lage'
}

// 拼音映射：每条 token 包含 initial (首字母) + full (全拼前 3 字符)
const pinyinMap = {
  // 万能 / 无色
  '珍宝':     { initial: 'zb',  full: 'zhen'   },
  '复制品':   { initial: 'fzp', full: 'fuzhi'  },
  '组构体':   { initial: 'zgzt',full: 'zugo'   },
  '衍生':     { initial: 'ys',  full: 'yans'   },
  // 白 (W)
  '士兵':     { initial: 'sb',  full: 'shib'   },
  '天使':     { initial: 'ts',  full: 'tian'   },
  '猫':       { initial: 'm',   full: 'mao'    },
  '狗':       { initial: 'g',   full: 'gou'    },
  '人类':     { initial: 'rl',  full: 'renl'   },
  '僧侣':     { initial: 'sl',  full: 'seng'   },
  '骑士':     { initial: 'qs',  full: 'qish'   },
  '狮鹫':     { initial: 'sy',  full: 'shij'   },
  '精怪':     { initial: 'jg',  full: 'jing'   },
  // 蓝 (U)
  '精灵':     { initial: 'jl',  full: 'jing'   },
  '龙兽':     { initial: 'll',  full: 'long'   },
  '虚影':     { initial: 'xy',  full: 'xuyi'   },
  '维多肯':   { initial: 'wdk', full: 'weid'   },
  '法师':     { initial: 'fs',  full: 'fash'   },
  '螃蟹':     { initial: 'px',  full: 'pang'   },
  '蛇':       { initial: 's',   full: 'she'    },
  '海怪':     { initial: 'hg',  full: 'haig'   },
  // 黑 (B)
  '灵俑':     { initial: 'ly',  full: 'ling'   },
  '鬼怪':     { initial: 'gg',  full: 'guig'   },
  '吸血鬼':   { initial: 'xxg', full: 'xixu'   },
  '蝙蝠':     { initial: 'bf',  full: 'bian'   },
  '骷髅':     { initial: 'kl',  full: 'kul'    },
  '恶魔':     { initial: 'em',  full: 'emo'    },
  '恐惧':     { initial: 'kj',  full: 'kong'   },
  '老鼠':     { initial: 'ls',  full: 'laos'   },
  '阴影':     { initial: 'yy',  full: 'yiny'   },
  '幽灵':     { initial: 'yl',  full: 'youl'   },
  // 红 (R)
  '野狼':     { initial: 'yl',  full: 'yela'   },
  '蜥蜴':     { initial: 'xy',  full: 'xiyi'   },
  '地精':     { initial: 'dj',  full: 'diji'   },
  '元素':     { initial: 'ys',  full: 'yuas'   },
  '龙':       { initial: 'l',   full: 'long'   },
  '巨魔':     { initial: 'jm',  full: 'jumo'   },
  '食人魔':   { initial: 'srm', full: 'shir'   },
  '火焰':     { initial: 'hy',  full: 'huoy'   },
  '半兽人':   { initial: 'brl', full: 'banr'   },
  // 绿 (G)
  '树妖':     { initial: 'sy',  full: 'shuy'   },
  '狼':       { initial: 'l',   full: 'lang'   },
  '昆虫':     { initial: 'kc',  full: 'kunc'   },
  '熊':       { initial: 'x',   full: 'xion'   },
  '象':       { initial: 'x',   full: 'xian'   },
  '蛇颈龙':   { initial: 'sjl', full: 'shej'   },
  '植物':     { initial: 'zw',  full: 'zhiw'   },
  '鹿':       { initial: 'l',   full: 'lu'     },
  '犀牛':     { initial: 'xn',  full: 'xini'   },
  '变形兽':   { initial: 'bx',  full: 'bian'   },
  '藤蔓':     { initial: 'tm',  full: 'tenm'   },
  '甲虫':     { initial: 'jc',  full: 'jiac'   },
  '德鲁伊':   { initial: 'dly', full: 'delu'   }
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
    tokens: [],
    tokenGroups: {},
    selectedColorFilter: 'all',
    groupCounts: {},
    totalCount: 0,
    filteredGroup: { tokens: [] },
    selectedToken: null,
    showModal: false,
    showCopyModal: false,
    copySearchQuery: '',
    copySearchResults: [],
    isCopySearching: false,
    allCards: [],
    tokenCards: [],
    availableSets: [],
    selectedSetCode: 'all',
    showSetPicker: false,
    selectedCardIndex: 0,
    isLoadingToken: false
  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    this.fetchTokenList()
  },

  onUnload() {
    this._pageActive = false
  },

  fetchTokenList() {
    this._pageActive = true
    api.request('/api/token/list', {}).then(res => {
      if (!this._pageActive) return
      if (res && res.tokens) {
        const colorOrder = ['C', 'W', 'U', 'B', 'R', 'G']
        const colorInfo = {
          'C': { name: '无色', symbol: 'C' },
          'W': { name: '白', symbol: 'W' },
          'U': { name: '蓝', symbol: 'U' },
          'B': { name: '黑', symbol: 'B' },
          'R': { name: '红', symbol: 'R' },
          'G': { name: '绿', symbol: 'G' }
        }
        const groups = {}
        colorOrder.forEach(color => {
          groups[color] = { name: colorInfo[color].name, symbol: colorInfo[color].symbol, tokens: [] }
        })
        res.tokens.forEach(token => {
          const color = token.color || 'C'
          if (groups[color]) {
            groups[color].tokens.push(token)
          }
        })
        // 计算每色数量和总数
        const groupCounts = {}
        let totalCount = 0
        colorOrder.forEach(color => {
          groupCounts[color] = groups[color].tokens.length
          totalCount += groups[color].tokens.length
        })
        this.setData({
          tokens: res.tokens,
          tokenGroups: groups,
          groupCounts: groupCounts,
          totalCount: totalCount
        })
        this.recomputeFilteredGroup()
      }
    }).catch(err => {
      console.error('fetchTokenList error', err)
    })
  },

  recomputeFilteredGroup() {
    const { tokenGroups, selectedColorFilter } = this.data
    if (selectedColorFilter === 'all') {
      // 全部：合并所有 token
      const all = []
      Object.values(tokenGroups).forEach(g => {
        all.push(...g.tokens)
      })
      this.setData({ filteredGroup: { tokens: all } })
    } else {
      this.setData({ filteredGroup: tokenGroups[selectedColorFilter] || { tokens: [] } })
    }
  },

  onFilterColor(e) {
    const color = e.currentTarget.dataset.color
    this.setData({ selectedColorFilter: color })
    this.recomputeFilteredGroup()
  },

  onClearSearch() {
    this.setData({
      searchQuery: '',
      showSearchResults: false,
      searchResults: []
    })
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  goToIndex() {
    wx.redirectTo({ url: '/pages/index/index' })
  },

  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  selectToken(e) {
    const token = (e.detail && e.detail.token) || (e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.token)
    if (!token) return
    if (token.type === 'copy') {
      this.setData({ showCopyModal: true, copySearchQuery: '', copySearchResults: [] })
      return
    }
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
    const searchName = translateToEn(token.enName)
    const encodedName = encodeURIComponent(searchName)

    const processCards = (cards, isFallback = false) => {
      if (!cards || cards.length === 0) {
        if (isFallback) {
          this.setData({ isLoadingToken: false, tokenCards: [], availableSets: [{ code: 'all', name: '全部' }] })
          wx.showToast({ title: '未找到该 Token，请尝试英文搜索', icon: 'none', duration: 2000 })
        }
        return
      }
      // 只保存必要字段，减小数据量
      const allCards = cards.map(card => ({
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
    }

    wx.request({
      url: `https://api.scryfall.com/cards/search?q=name:${encodedName}%20is:token&unique=art&order=released`,
      method: 'GET',
      header: {
        'User-Agent': 'mtgAsk-miniprogram/1.0 (https://github.com/raymondEEEEMMMM)',
        'Accept': 'application/json'
      },
      success: res => {
        if (res.statusCode === 404 || res.statusCode === 400 || !res.data || !res.data.data || res.data.data.length === 0) {
          this.setData({ isLoadingToken: false, tokenCards: [], availableSets: [{ code: 'all', name: '全部' }] })
          wx.showToast({ title: '未找到该 Token，请尝试英文搜索', icon: 'none', duration: 2000 })
          return
        }
        processCards(res.data.data)
      },
      fail: (err) => {
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

    const searchName = encodeURIComponent(translateToEn(query))
    wx.request({
      url: `https://api.scryfall.com/cards/search?q=t:${searchName}%20is:token%20-s:fnm&unique=art&order=released`,
      method: 'GET',
      header: {
        'User-Agent': 'mtgAsk-miniprogram/1.0 (https://github.com/raymondEEEEMMMM)',
        'Accept': 'application/json'
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
  },

  onCopySearch(e) {
    const query = e.detail.value.trim()
    this.setData({ copySearchQuery: query })
    if (!query) {
      this.setData({ copySearchResults: [] })
      return
    }
    this.setData({ isCopySearching: true })
    api.searchCard(query, 1, 10).then(res => {
      if (!this._pageActive) return
      const cards = ((res && res.items) ? res.items : []).slice(0, 9)
      this.setData({ copySearchResults: cards, isCopySearching: false })
    }).catch(() => {
      if (!this._pageActive) return
      this.setData({ isCopySearching: false })
      wx.showToast({ title: '搜索失败，请重试', icon: 'none' })
    })
  },

  selectCopyCard(e) {
    const card = e.currentTarget.dataset.card
    const imageNormal = card.zhs_image_uris?.normal || card.image_uris?.normal || ''
    const imageSmall = card.zhs_image_uris?.small || card.image_uris?.small || imageNormal
    const cardData = {
      name: card.name,
      set: card.set,
      set_name: card.set_name,
      image_uris: { normal: imageNormal, small: imageSmall },
      isCopy: true
    }
    const cardStr = encodeURIComponent(JSON.stringify(cardData))
    this.setData({ showCopyModal: false, copySearchQuery: '', copySearchResults: [] })
    wx.navigateTo({ url: '/pages/token-generate/token-generate?card=' + cardStr })
  },

  closeCopyModal() {
    this.setData({ showCopyModal: false, copySearchQuery: '', copySearchResults: [] })
  },

  noop() {}
})
