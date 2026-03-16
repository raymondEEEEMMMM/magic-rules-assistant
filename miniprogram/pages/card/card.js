// pages/card/card.js
const app = getApp()
const API_BASE = 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com'

Page({
  data: {
    keyword: '',
    cards: [],
    loading: false,
    searchDone: false,
    showDetail: false,
    currentCard: null,
    useApi: false // 是否使用API
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

  // 切换API/本地模式
  toggleApiMode() {
    this.setData({
      useApi: !this.data.useApi
    })
    wx.showToast({
      title: this.data.useApi ? '已切换为API模式' : '已切换为本地模式',
      icon: 'none'
    })
  },

  onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.setData({ 
      loading: true,
      searchDone: false 
    })

    if (this.data.useApi) {
      this.performApiSearch(keyword)
    } else {
      this.performLocalSearch(keyword)
    }
  },

  // API搜索实现
  performApiSearch(keyword) {
    wx.showLoading({ title: '搜索中...' })

    wx.request({
      url: `${API_BASE}/wechat/api/mtgch/search`,
      data: {
        q: keyword,
        page: 1,
        page_size: 10
      },
      method: 'GET',
      success: (res) => {
        wx.hideLoading()
        console.log('卡牌搜索API响应:', res.data)

        const apiData = res.data

        // 检查错误响应
        if (apiData && apiData.error) {
          this.setData({
            loading: false,
            searchDone: true,
            cards: []
          })
          wx.showToast({
            title: apiData.error,
            icon: 'none'
          })
          return
        }

        // 正常响应：{ total, page, page_size, items: [...] }
        if (apiData && apiData.items) {
          const cards = apiData.items.map(item => ({
            id: item.id,
            name: item.name,
            manaCost: item.mana_cost || '',
            type: item.type || '',
            text: item.oracle_text || '',
            power: item.power || '',
            toughness: item.toughness || '',
            setName: item.set_name || '',
            collectorNumber: item.collector_number || '',
            rarity: item.rarity || ''
          }))

          this.setData({
            loading: false,
            searchDone: true,
            cards: cards
          })

          if (cards.length > 0) {
            wx.showToast({
              title: `找到 ${cards.length} 张卡牌`,
              icon: 'success'
            })
          }
        } else {
          this.setData({
            loading: false,
            searchDone: true,
            cards: []
          })
          wx.showToast({
            title: '未找到相关卡牌',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('卡牌搜索API错误:', err)
        this.setData({
          loading: false,
          searchDone: true,
          cards: []
        })
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
      }
    })
  },

  // 本地搜索实现
  performLocalSearch(keyword) {
    setTimeout(() => {
      const mockCards = this.getMockCards()
      const results = mockCards.filter(card => 
        card.name.toLowerCase().includes(keyword.toLowerCase()) ||
        card.text.toLowerCase().includes(keyword.toLowerCase()) ||
        card.type.toLowerCase().includes(keyword.toLowerCase())
      )

      this.setData({
        loading: false,
        searchDone: true,
        cards: results
      })

      if (results.length === 0) {
        wx.showToast({
          title: '未找到相关卡牌',
          icon: 'none'
        })
      }
    }, 300)
  },

  // 获取模拟卡牌数据
  getMockCards() {
    return [
      {
        name: '黑绿霸主',
        manaCost: '{2}{B}{G}',
        type: '生物 — 霸主',
        text: '当黑绿霸主进入战场时，你可以从你的牌库中寻找一张沼泽牌或森林牌，将其横置放进战场，然后将你的牌库洗牌。',
        power: '4',
        toughness: '4'
      },
      {
        name: '红蓝法师',
        manaCost: '{U}{R}',
        type: '生物 — 人类 法师',
        text: '飞行\n每当红蓝法师成为咒语或异能的目标时，你可以掷硬币。如果是正面，反击该咒语或异能。',
        power: '2',
        toughness: '2'
      },
      {
        name: '白绿野兽',
        manaCost: '{3}{G}{W}',
        type: '生物 — 野兽',
        text: '践踏\n每当白绿野兽造成战斗伤害时，你可以获得等量的生命。',
        power: '5',
        toughness: '5'
      },
      {
        name: '黑红恶魔',
        manaCost: '{2}{B}{R}',
        type: '生物 — 恶魔',
        text: '飞行，先攻\n当黑红恶魔进入战场时，它对目标玩家造成3点伤害。',
        power: '3',
        toughness: '3'
      },
      {
        name: '蓝白控制',
        manaCost: '{2}{U}{W}',
        type: '生物 — 史力斯 法师',
        text: '闪现\n当蓝白控制进入战场时，你可以反击目标咒语，如果该咒语的目标是你。',
        power: '2',
        toughness: '4'
      },
      {
        name: '绿红战士',
        manaCost: '{1}{G}{R}',
        type: '生物 — 人类 战士',
        text: '敏捷\n每当绿红战士攻击时，它获得+2/+0直到回合结束。',
        power: '2',
        toughness: '2'
      },
      {
        name: '黑白结界',
        manaCost: '{2}{B}{W}',
        type: '结界',
        text: '在每位玩家的 upkeep 开始时，该玩家失去1点生命，然后你获得1点生命。',
        power: '',
        toughness: ''
      },
      {
        name: '蓝红瞬间',
        manaCost: '{U}{R}',
        type: '瞬间',
        text: '反击目标咒语，如果其法术力费用不等于3。如果这样做了，蓝红瞬间对目标生物或牌手造成2点伤害。',
        power: '',
        toughness: ''
      }
    ]
  },

  showCardDetail(e) {
    const card = e.currentTarget.dataset.card

    // 如果是 API 模式且有卡牌 ID，尝试获取完整详情
    if (this.data.useApi && card.id) {
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
        console.log('卡牌详情API响应:', res.data)

        const apiData = res.data

        // 检查错误响应
        if (apiData && apiData.error) {
          wx.showToast({
            title: apiData.error,
            icon: 'none'
          })
          return
        }

        // 正常响应：卡牌详情对象
        if (apiData && apiData.name) {
          this.setData({
            currentCard: {
              id: apiData.id,
              name: apiData.name,
              manaCost: apiData.mana_cost || '',
              type: apiData.type || '',
              text: apiData.oracle_text || '',
              power: apiData.power || '',
              toughness: apiData.toughness || '',
              setName: apiData.set_name || '',
              collectorNumber: apiData.collector_number || '',
              rarity: apiData.rarity || '',
              imageUrl: apiData.image_uris?.normal || ''
            },
            showDetail: true
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('卡牌详情API错误:', err)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    })
  },

  // 获取随机卡牌
  getRandomCard() {
    wx.showLoading({ title: '获取中...' })

    wx.request({
      url: `${API_BASE}/wechat/api/mtgch/random`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading()
        console.log('随机卡牌API响应:', res.data)

        const apiData = res.data

        // 检查错误响应
        if (apiData && apiData.error) {
          wx.showToast({
            title: apiData.error,
            icon: 'none'
          })
          return
        }

        // 正常响应：随机卡牌对象
        if (apiData && apiData.name) {
          this.setData({
            currentCard: {
              id: apiData.id,
              name: apiData.name,
              manaCost: apiData.mana_cost || '',
              type: apiData.type || '',
              text: apiData.oracle_text || '',
              power: apiData.power || '',
              toughness: apiData.toughness || '',
              setName: apiData.set_name || '',
              collectorNumber: apiData.collector_number || '',
              rarity: apiData.rarity || '',
              imageUrl: apiData.image_uris?.normal || ''
            },
            showDetail: true,
            keyword: ''
          })

          wx.showToast({
            title: '已获取随机卡牌',
            icon: 'success'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('随机卡牌API错误:', err)
        wx.showToast({
          title: '获取失败',
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

  preventClose() {
    // 阻止关闭
  }
})
