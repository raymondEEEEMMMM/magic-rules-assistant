// pages/decks/decks.js
const app = getApp()

// 中英对照表（复用 token 页面的）
const cnToEnMap = {
  '珍宝': 'Treasure', '闪电击': 'Lightning Bolt', '黑莲花': 'Black Lotus',
  '山脉': 'Mountain', '海岛': 'Island', '平原': 'Plains', '森林': 'Forest', '沼泽': 'Swamp',
  '士兵': 'Soldier', '天使': 'Angel', '精灵': 'Elf', '野狼': 'Wolf', '猫': 'Cat',
  '龙': 'Dragon', '鬼怪': 'Goblin', '吸血鬼': 'Vampire', '灵俑': 'Zombie'
}

function translateToEn(cn) {
  return cnToEnMap[cn] || cn
}

// Moxfield 格式解析：`1 CardName (SET) Number *F*`
function parseMoxfieldLine(line) {
  const match = line.trim().match(/^(\d+)\s+(.+?)\s+\(([^)]+)\)\s+(\d+|\S+)/)
  if (!match) return null
  return {
    count: parseInt(match[1]),
    name: match[2].trim(),
    set: match[3].trim()
  }
}

// 解析套牌文本
// cardFormat: '自动识别' | '平铺' | 'MTGA' | 'Moxfield'
function parseDeckText(text, cardFormat = '自动识别') {
  const lines = text.trim().split('\n')
  const cards = []
  const errors = []
  let commander = null

  let isMoxfield = false
  let isMTGA = false

  if (cardFormat === 'Moxfield') {
    isMoxfield = true
  } else if (cardFormat === 'MTGA') {
    isMTGA = true
  } else if (cardFormat === '自动识别') {
    const moxfieldCount = lines.filter(l => parseMoxfieldLine(l)).length
    isMoxfield = moxfieldCount >= lines.filter(l => l.trim()).length * 0.5
    const commanderIdx = lines.findIndex(l => l.trim() === 'Commander:')
    isMTGA = commanderIdx !== -1
  }
  // cardFormat === '平铺' 时，isMoxfield 和 isMTGA 均为 false

  let inCommander = false

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue

    if (line === 'About' || line.startsWith('Name ')) continue
    if (line === 'Deck') { inCommander = false; continue }
    if (line === 'Commander:') { inCommander = true; continue }

    if (isMoxfield) {
      const parsed = parseMoxfieldLine(line)
      if (parsed) {
        const name = translateToEn(parsed.name)
        if (parsed.count > 0) {
          cards.push({ name, count: parsed.count, set: parsed.set })
        }
        continue
      }
      errors.push(`第${i + 1}行无法识别: ${line}`)
      continue
    }

    if (isMTGA && inCommander) {
      const match = line.match(/^(\d+)x?\s+(.+)$/)
      if (match) {
        commander = translateToEn(match[2].trim())
      }
      continue
    }

    const match = line.match(/^(\d+)x?\s+(.+)$/)
    if (match) {
      const count = parseInt(match[1])
      let name = translateToEn(match[2].trim())
      if (count > 0) {
        cards.push({ name, count })
      }
      continue
    }

    if (line.length > 0) {
      errors.push(`第${i + 1}行无法识别: ${line}`)
    }
  }

  return { cards, errors, commander }
}

// 计算总张数
function calcTotalCards(cards) {
  return cards.reduce((sum, card) => sum + card.count, 0)
}

// 批量查询 Scryfall 获取 CMC（用于 AVG CMC 计算）
// 每次最多 75 张，分批查询
async function fetchCMCFromScryfall(cards) {
  const identifiers = cards.map(c => ({ name: c.name }))
  const results = {}

  const chunkSize = 75
  for (let i = 0; i < identifiers.length; i += chunkSize) {
    const chunk = identifiers.slice(i, i + chunkSize)
    try {
      const resp = await wx.request({
        url: 'https://api.scryfall.com/cards/collection',
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        data: JSON.stringify({ identifiers: chunk }),
        timeout: 30000
      })
      const data = resp && resp.data
      if (data && data.data) {
        for (const card of data.data) {
          const key = card.name.toLowerCase()
          results[key] = card.cmc || 0
        }
      }
    } catch (e) {
      console.error('Scryfall batch query failed', e)
    }
  }
  return results
}

// 计算 AVG CMC
function calcAvgCMC(cards, cmcMap) {
  let totalCMC = 0
  let totalCards = 0
  for (const card of cards) {
    const mv = cmcMap[card.name.toLowerCase()] || 0
    totalCMC += mv * card.count
    totalCards += card.count
  }
  return totalCards > 0 ? (totalCMC / totalCards).toFixed(2) : '0.00'
}

Page({
  data: {
    isLightTheme: false,
    decks: [],
    showImportModal: false,
    importText: '',
    importUrl: '',
    parseResult: null,
    parseErrors: [],
    showDeckModal: false,
    selectedDeck: null,
    editingName: '',
    editingFormat: '标准',
    editingCommander: '',
    editingCardFormat: '自动识别',
    formats: ['指挥官', '标准', '摩登', '先驱', '薪传', '其他'],
    cardFormats: ['自动识别', '平铺', 'MTGA', 'Moxfield'],
    commanderResults: [],
    commanderInput: '',

  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    this.loadDecks()
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 初始化 - 直接加载套牌
  initOpenid() {
    // 直接加载套牌，CloudBase 会自动处理 openid
    this.loadDecks()
  },

  goBack() {
    wx.navigateBack()
  },

  // 阻止事件冒泡（阻止弹窗关闭）
  catchInner() {},

  // 套牌内容输入
  onImportTextInput(e) {
    this.setData({ importText: e.detail.value })
  },

  // 加载套牌列表（从云数据库）
  loadDecks() {
    console.log('CODEBUDDY_DEBUG loadDecks called')
    const db = app.globalData.db
    db.collection('decks').orderBy('createdAt', 'desc').get().then(res => {
      const decks = res.data || []
      // 本地也缓存一份
      wx.setStorageSync('mtg_decks', decks)
      this.setData({ decks })
    }).catch(err => {
      console.error('loadDecks error', err)
      // 失败时读本地
      const decks = wx.getStorageSync('mtg_decks') || []
      this.setData({ decks })
    })
  },

  // 保存单条套牌到云数据库
  saveDeckToCloud(deck) {
    const db = app.globalData.db
    return db.collection('decks').add({ data: deck })
  },

  // 从云数据库删除
  deleteDeckFromCloud(id) {
    const db = app.globalData.db
    return db.collection('decks').doc(id).remove()
  },

  // 打开导入弹窗
  showImport() {
    this.setData({
      showImportModal: true,
      importText: '',
      parseResult: null,
      parseErrors: [],
      editingName: '',
      editingCommander: '',
      editingFormat: '标准',
      editingCardFormat: '自动识别',
      commanderResults: [],
      commanderInput: ''
    })
  },

  // 关闭导入弹窗
  closeImport() {
    this.setData({ showImportModal: false })
  },

  // 解析套牌文本
  async parseImportText() {
    const { importText, editingCardFormat } = this.data
    if (!importText.trim()) {
      wx.showToast({ title: '请输入套牌内容', icon: 'none' })
      return
    }

    const { cards, commander } = parseDeckText(importText, editingCardFormat)

    if (cards.length === 0) {
      wx.showToast({ title: '未识别到有效卡牌', icon: 'none' })
      return
    }

    // 查询 Scryfall 获取 CMC（用于 AVG CMC）
    let avgCMC = '0.00'
    wx.showLoading({ title: '计算 CMC...', mask: true })
    try {
      const cmcMap = await fetchCMCFromScryfall(cards)
      avgCMC = calcAvgCMC(cards, cmcMap)
    } catch (e) {
      console.error('CMC fetch error', e)
    }
    wx.hideLoading()

    this.setData({
      parseResult: { cards, total: calcTotalCards(cards), avgCMC, commander },
      parseErrors: errors,
      editingCommander: commander || ''
    })
  },

  // 检查套牌名称是否重复
  checkDuplicateName(name) {
    return this.data.decks.some(d => d.name === name)
  },

  // 确认导入（自动解析）
  async confirmImport() {
    const { importText, editingName, editingFormat, editingCommander, editingCardFormat } = this.data
    if (!importText.trim()) {
      wx.showToast({ title: '请输入套牌内容', icon: 'none' })
      return
    }

    wx.showLoading({ title: '解析中...', mask: true })
    const { cards, commander } = parseDeckText(importText, editingCardFormat)
    console.log('CODEBUDDY_DEBUG confirmImport cards=', JSON.stringify(cards).substring(0, 500))
    if (cards.length === 0) {
      wx.hideLoading()
      wx.showToast({ title: '未识别到有效卡牌', icon: 'none' })
      return
    }

    // 自动补全套牌名称（如果为空）
    let finalName = editingName.trim()
    if (!finalName && cards.length > 0) {
      finalName = cards[0].name
      this.setData({ editingName: finalName })
      wx.showToast({ title: `已使用「${finalName}」作为套牌名`, icon: 'none', duration: 2000 })
    }

    if (!finalName) {
      wx.hideLoading()
      wx.showToast({ title: '请输入套牌名称', icon: 'none' })
      return
    }

    let avgCMC = '0.00'
    let cmcFailed = false
    try {
      const res = await wx.cloud.callFunction({
        name: 'mtgAsk',
        data: {
          httpMethod: 'POST',
          path: '/api/deck/cmc',
          cards: cards
        }
      })
      const result = res.result
      if (result && result.body) {
        try {
          const body = typeof result.body === 'string' ? JSON.parse(result.body) : result.body
          if (body.avgCMC) {
            avgCMC = body.avgCMC
            console.log('CODEBUDDY_DEBUG CMC result avgCMC=', body.avgCMC, 'cmcMap=', JSON.stringify(body.cmcMap).substring(0, 300))
            if (Object.keys(body.cmcMap || {}).length === 0) cmcFailed = true
          } else {
            cmcFailed = true
          }
        } catch (e) {
          console.error('Parse CMC result failed', e)
          cmcFailed = true
        }
      } else {
        cmcFailed = true
        console.log('CODEBUDDY_DEBUG CMC failed - result=', JSON.stringify(result).substring(0, 200))
      }
    } catch (e) {
      console.error('CMC fetch error', e)
      cmcFailed = true
    }

    // 检查重名
    if (this.checkDuplicateName(finalName)) {
      wx.hideLoading()
      wx.showModal({
        title: '套牌名称重复',
        content: `已存在名为「${finalName}」的套牌，是否覆盖？`,
        confirmText: '覆盖',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            // 删除旧套牌后重新导入
            this.overwriteDeck(finalName, { name: finalName, format: editingFormat, commander: editingCommander || commander || '', cards, totalCards: calcTotalCards(cards), avgCMC })
          } else {
            wx.showToast({ title: '已取消', icon: 'none' })
          }
        }
      })
      return
    }

    const newDeck = {
      // openid 由 CloudBase 自动填充 (_openid)
      name: finalName,
      format: editingFormat,
      commander: editingCommander || commander || '',
      cards: cards,
      totalCards: calcTotalCards(cards),
      avgCMC: avgCMC,
      createdAt: new Date().toISOString()
    }
    console.log('CODEBUDDY_DEBUG newDeck commander info:', 'editingCommander=', editingCommander, 'commander(from parse)=', commander, 'final=', newDeck.commander)

    if (cmcFailed) {
      wx.showToast({ title: 'AVG CMC 计算失败，已设为0', icon: 'none', duration: 2000 })
    }

    wx.showLoading({ title: '保存中...', mask: true })
    this.saveDeckToCloud(newDeck).then(res => {
      newDeck._id = res._id
      const decks = [newDeck, ...this.data.decks]
      wx.setStorageSync('mtg_decks', decks)
      this.setData({ decks })
      this.closeImport()
      wx.hideLoading()
      wx.showToast({ title: '导入成功', icon: 'success' })
    }).catch(err => {
      wx.hideLoading()
      console.error('saveDeckToCloud error', err)
      wx.showToast({ title: '保存失败', icon: 'none' })
    })
  },

  // 覆盖同名套牌
  async overwriteDeck(nameToOverwrite, deckData) {
    const db = app.globalData.db
    wx.showLoading({ title: '覆盖中...', mask: true })
    try {
      // 先查询要删除的套牌
      const res = await db.collection('decks').where({ name: nameToOverwrite }).get()
      if (res.data && res.data.length > 0) {
        const oldDeck = res.data[0]
        await db.collection('decks').doc(oldDeck._id).remove()
      }
      // 保存新套牌
      deckData.createdAt = new Date().toISOString()
      const saveRes = await this.saveDeckToCloud(deckData)
      deckData._id = saveRes._id
      const decks = [deckData, ...this.data.decks.filter(d => d.name !== nameToOverwrite)]
      wx.setStorageSync('mtg_decks', decks)
      this.setData({ decks })
      this.closeImport()
      wx.hideLoading()
      wx.showToast({ title: '已覆盖', icon: 'success' })
    } catch (e) {
      wx.hideLoading()
      console.error('overwriteDeck error', e)
      wx.showToast({ title: '覆盖失败', icon: 'none' })
    }
  },

  // 设置套牌名称
  setDeckName(e) {
    this.setData({ editingName: e.detail.value })
  },

  // 设置指挥官
  setCommander(e) {
    this.setData({ editingCommander: e.detail.value })
  },

  // 选择赛制
  selectFormat(e) {
    const index = parseInt(e.detail.value)
    this.setData({ editingFormat: this.data.formats[index] })
  },

  // 选择卡牌格式
  selectCardFormat(e) {
    const index = parseInt(e.detail.value)
    this.setData({ editingCardFormat: this.data.cardFormats[index] })
  },

  // 指挥官搜索输入
  onCommanderInput(e) {
    this.setData({ commanderInput: e.detail.value })
  },

  // 搜索指挥官
  searchCommander() {
    const query = this.data.commanderInput.trim()
    if (!query) return
    wx.showLoading({ title: '搜索中...', mask: true })
    wx.request({
      url: 'https://api.scryfall.com/cards/search',
      data: { q: query + ' t:legendary' },
      timeout: 15000,
      success: (res) => {
        wx.hideLoading()
        if (res.data && res.data.data && res.data.data.length > 0) {
          const results = res.data.data.slice(0, 8).map(card => ({
            name: card.name,
            image: card.image_uris ? (card.image_uris.small || card.image_uris.normal) : '',
            type_line: card.type_line || ''
          }))
          this.setData({ commanderResults: results })
        } else {
          this.setData({ commanderResults: [] })
          wx.showToast({ title: '未找到', icon: 'none' })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '搜索失败', icon: 'none' })
      }
    })
  },

  // 选择指挥官
  selectCommander(e) {
    const index = parseInt(e.currentTarget.dataset.index)
    const card = this.data.commanderResults[index]
    if (card) {
      this.setData({
        editingCommander: card.name,
        commanderResults: [],
        commanderInput: ''
      })
    }
  },

  // 预览套牌
  previewDeck(e) {
    const deck = e.currentTarget.dataset.deck
    this.setData({
      showDeckModal: true,
      selectedDeck: deck
    })
  },

  // 关闭预览
  closeDeckPreview() {
    this.setData({ showDeckModal: false, selectedDeck: null })
  },

  // 跳转到卡组详情页
  goToDeckDetail() {
    const { selectedDeck } = this.data
    if (!selectedDeck) return
    const deckStr = encodeURIComponent(JSON.stringify(selectedDeck))
    wx.navigateTo({
      url: `/pages/deck-detail/deck-detail?deck=${deckStr}`
    })
  },

  // 关闭预览
  closeDeckPreview() {
    this.setData({ showDeckModal: false, selectedDeck: null })
  },

  // 删除套牌
  deleteDeck(e) {
    const deck = this.data.selectedDeck
    if (!deck) return
    wx.showModal({
      title: '删除套牌',
      content: '确定要删除这个套牌吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...', mask: true })
          this.deleteDeckFromCloud(deck._id).then(() => {
            const decks = this.data.decks.filter(d => d._id !== deck._id)
            wx.setStorageSync('mtg_decks', decks)
            this.setData({ decks })
            this.closeDeckPreview()
            wx.hideLoading()
            wx.showToast({ title: '已删除', icon: 'success' })
          }).catch(err => {
            wx.hideLoading()
            console.error('deleteDeckFromCloud error', err)
            wx.showToast({ title: '删除失败', icon: 'none' })
          })
        }
      }
    })
  },

  // 复制套牌（导出）
  exportDeck() {
    const { selectedDeck } = this.data
    if (!selectedDeck) return

    const text = selectedDeck.cards
      .map(c => `${c.count} ${c.name}`)
      .join('\n')

    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' })
      }
    })
  },

  // 粘贴套牌（从剪贴板导入）
  pasteFromClipboard() {
    wx.getClipboardData({
      success: (res) => {
        if (res.data) {
          this.setData({ importText: res.data })
          wx.showToast({ title: '已粘贴', icon: 'success' })
        }
      }
    })
  },

  // URL 输入
  onImportUrlInput(e) {
    this.setData({ importUrl: e.detail.value })
  },

  // 粘贴 URL
  pasteUrlFromClipboard() {
    wx.getClipboardData({
      success: (res) => {
        if (res.data && (res.data.includes('mtggoldfish') || res.data.includes('moxfield') || res.data.includes('goldfish'))) {
          this.setData({ importUrl: res.data })
          wx.showToast({ title: 'URL已粘贴', icon: 'success' })
        } else if (res.data) {
          this.setData({ importUrl: res.data })
          wx.showToast({ title: '已粘贴', icon: 'success' })
        }
      }
    })
  },

  // 从 URL 导入套牌
  importFromUrl() {
    const { importUrl } = this.data
    if (!importUrl) return

    // 检测 URL 类型
    if (importUrl.includes('mtggoldfish')) {
      this.fetchMTGGoldfishDeck(importUrl)
    } else if (importUrl.includes('moxfield')) {
      this.fetchMoxfieldDeck(importUrl)
    } else {
      wx.showToast({ title: '暂不支持该URL', icon: 'none' })
    }
  },

  // 解析 MTGGoldfish URL 获取套牌
  fetchMTGGoldfishDeck(url) {
    wx.showLoading({ title: '解析中...', mask: true })
    wx.cloud.callFunction({
      name: 'mtgAsk',
      data: {
        httpMethod: 'GET',
        path: '/api/deck/parse-url',
        url: url
      }
    }).then(res => {
      wx.hideLoading()
      const result = res.result
      if (result && result.success && result.cards) {
        this.setData({
          importText: result.cards.map(c => `${c.count} ${c.name}`).join('\n'),
          editingName: result.name || '',
          importUrl: ''
        })
        wx.showToast({ title: '导入成功', icon: 'success' })
      } else {
        wx.showToast({ title: result.error || '解析失败', icon: 'none' })
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('fetchMTGGoldfishDeck error', err)
      wx.showToast({ title: '解析失败', icon: 'none' })
    })
  },

  // 解析 Moxfield URL 获取套牌
  fetchMoxfieldDeck(url) {
    wx.showLoading({ title: '解析中...', mask: true })
    wx.cloud.callFunction({
      name: 'mtgAsk',
      data: {
        httpMethod: 'GET',
        path: '/api/deck/parse-url',
        url: url
      }
    }).then(res => {
      wx.hideLoading()
      const result = res.result
      if (result && result.success && result.cards) {
        this.setData({
          importText: result.cards.map(c => `${c.count} ${c.name}`).join('\n'),
          editingName: result.name || '',
          editingCardFormat: 'Moxfield',
          importUrl: ''
        })
        wx.showToast({ title: '导入成功', icon: 'success' })
      } else {
        wx.showToast({ title: result.error || '解析失败', icon: 'none' })
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('fetchMoxfieldDeck error', err)
      wx.showToast({ title: '解析失败', icon: 'none' })
    })
  }
})
