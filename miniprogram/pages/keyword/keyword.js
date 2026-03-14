// pages/keyword/keyword.js
const app = getApp()
const API_BASE = 'https://magic-rules-assistant-0a1904c329.tcb.qcloud.la'

Page({
  data: {
    keyword: '',
    keywords: [],
    keywordDetail: null,
    searchDone: false,
    useApi: false, // 是否使用后端API
    autoTesting: false, // 是否正在自动化测试
    testResults: [] // 测试结果
  },

  onLoad(options) {
    if (options.keyword) {
      this.setData({
        keyword: decodeURIComponent(options.keyword)
      })
      this.onSearch()
    } else if (options.autoTest === 'true') {
      // 自动化测试模式
      this.startAutoTest()
    } else {
      // 加载关键词列表
      this.loadKeywordList()
    }
  },

  onInput(e) {
    this.setData({ 
      keyword: e.detail.value,
      keywordDetail: null
    })
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
    wx.showLoading({ title: '查询中...' })

    wx.request({
      url: `${API_BASE}/api/keyword`,
      data: { k: keyword },
      method: 'GET',
      success: (res) => {
        wx.hideLoading()
        console.log('关键词API响应:', res.data)

        const apiData = res.data

        // 检查错误响应
        if (apiData && apiData.error) {
          this.setData({
            searchDone: true,
            keywordDetail: null
          })
          wx.showToast({
            title: apiData.error,
            icon: 'none'
          })
          return
        }

        // 正常响应：{ keyword: "Flying", result: { keyword_name, description, full_text } }
        if (apiData && apiData.keyword && apiData.result) {
          const result = apiData.result
          this.setData({
            searchDone: true,
            keywordDetail: {
              name: result.keyword_name || apiData.keyword,
              englishName: apiData.keyword,
              description: result.description || result.full_text || '暂无说明',
              fullText: result.full_text || '',
              examples: [],
              relatedCards: []
            }
          })
        } else {
          this.setData({
            searchDone: true,
            keywordDetail: null
          })
          wx.showToast({
            title: '未找到关键词',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('关键词API错误:', err)
        this.setData({
          searchDone: true,
          keywordDetail: null
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
      const detail = this.getMockKeywordDetail(keyword)
      this.setData({
        searchDone: true,
        keywordDetail: detail || null
      })

      if (!detail) {
        wx.showToast({
          title: '未找到关键词',
          icon: 'none'
        })
      }
    }, 300)
  },

  // 获取模拟关键词详情
  getMockKeywordDetail(keyword) {
    const keywordDetails = {
      '飞行': {
        name: '飞行',
        englishName: 'Flying',
        description: '具有飞行的生物只能被其他具有飞行或延势的生物阻挡。',
        examples: [
          '一只具有飞行的3/3生物可以攻击而不被没有飞行或延势的生物阻挡。',
          '如果你的生物没有飞行，即使它有无限力量，也无法阻挡飞行的生物。'
        ],
        relatedCards: ['天使', '龙', '鸟妖']
      },
      '死触': {
        name: '死触',
        englishName: 'Deathtouch',
        description: '具有死触的任何生物只要对另一个生物造成大于0的伤害，就会造成等量的伤害。',
        examples: [
          '一只1/1具有死触的生物攻击一只5/5的生物，即使只造成1点伤害，也会消灭那只5/5生物。',
          '死触对鹏洛客和牌手没有特殊效果，只对生物有效。'
        ],
        relatedCards: ['腐化', '死亡之影']
      },
      '警戒': {
        name: '警戒',
        englishName: 'Vigilance',
        description: '警戒可以让生物在攻击时不会横置，并且在攻击者步骤后仍能阻挡。',
        examples: [
          '具有警戒的生物可以在攻击后立即阻挡对手的生物。',
          '警戒与先攻、双重打击等关键词可以很好地配合。'
        ],
        relatedCards: ['圣堂护卫', '天空守护者']
      },
      '先攻': {
        name: '先攻',
        englishName: 'First Strike',
        description: '具有先攻的生物在战斗伤害步骤中先于没有先攻的生物造成战斗伤害。',
        examples: [
          '一只2/2具有先攻的生物与一只2/2生物战斗，先攻生物先造成2点伤害，消灭对手生物，而不会受到伤害。',
          '先攻与高力量生物的配合可以造成一击必杀的效果。'
        ],
        relatedCards: ['白色骑士', '红色战士']
      },
      '闪现': {
        name: '闪现',
        englishName: 'Flash',
        description: '你可以在任何时候施放具有闪现的咒语，就像它是瞬间一样。',
        examples: [
          '可以在对手的回合中施放闪现生物，用于阻挡或出其不意。',
          '闪现让卡牌的时机更加灵活，适合控制型套牌。'
        ],
        relatedCards: ['树妖', '史力斯法师']
      },
      '践踏': {
        name: '践踏',
        englishName: 'Trample',
        description: '当具有践踏的生物在造成战斗伤害时，若其力量大于阻挡生物的防御力，超出的伤害会分配给受击牌手或鹏洛客。',
        examples: [
          '一只5/5践踏生物被2/2生物阻挡，它对阻挡者造成2点伤害，对对手造成3点伤害。',
          '践踏让大生物不会被小生物"浪费"伤害。'
        ],
        relatedCards: ['犀牛', '大象']
      },
      '系命': {
        name: '系命',
        englishName: 'Lifelink',
        description: '具有系命的永久物、咒语或能力在造成伤害的同时，会使你获得等量的生命。',
        examples: [
          '一只3/3具有系命的生物攻击对手，造成3点伤害，你同时获得3点生命。',
          '系命与高力量生物的配合可以快速恢复生命值。'
        ],
        relatedCards: ['吸血鬼', '天使']
      }
    }

    // 模糊匹配
    const lowerKeyword = keyword.toLowerCase()
    for (const [key, value] of Object.entries(keywordDetails)) {
      if (key.toLowerCase().includes(lowerKeyword) || 
          value.englishName.toLowerCase().includes(lowerKeyword)) {
        return value
      }
    }

    return null
  },

  loadKeywordList() {
    // 预定义常用关键词列表
    const commonKeywords = [
      { name: '飞行', english: 'Flying' },
      { name: '死触', english: 'Deathtouch' },
      { name: '警戒', english: 'Vigilance' },
      { name: '先攻', english: 'First Strike' },
      { name: '闪现', english: 'Flash' },
      { name: '敏捷', english: 'Haste' },
      { name: '践踏', english: 'Trample' },
      { name: '系命', english: 'Lifelink' },
      { name: '延势', english: 'Reach' },
      { name: '辟邪', english: 'Hexproof' },
      { name: '不灭', english: 'Indestructible' },
      { name: '威慑', english: 'Menace' },
      { name: '双重打击', english: 'Double Strike' },
      { name: '连击', english: 'Double Strike' },
      { name: '闪避', english: 'Evasion' }
    ]

    this.setData({ keywords: commonKeywords })
  },

  viewKeyword(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.onSearch()
  },

  goBack() {
    this.setData({
      keywordDetail: null,
      keyword: ''
    })
    this.loadKeywordList()
  },

  // 开始自动化测试
  async startAutoTest() {
    if (this.data.autoTesting) return
    
    this.setData({
      autoTesting: true,
      testResults: []
    })

    // 测试步骤
    const testSteps = [
      {
        name: '步骤1: 加载关键词列表',
        action: () => {
          this.loadKeywordList()
          return this.data.keywords.length > 0
        }
      },
      {
        name: '步骤2: 模拟点击"系命"关键词',
        action: () => {
          const lifelinkKeyword = this.data.keywords.find(k => k.name === '系命')
          if (lifelinkKeyword) {
            this.setData({ keyword: lifelinkKeyword.name })
            return true
          }
          return false
        }
      },
      {
        name: '步骤3: 执行搜索查询',
        action: () => {
          this.onSearch()
          return true
        }
      },
      {
        name: '步骤4: 验证搜索结果',
        action: () => {
          return new Promise((resolve) => {
            setTimeout(() => {
              const hasDetail = this.data.keywordDetail !== null
              const correctKeyword = this.data.keywordDetail && 
                                   this.data.keywordDetail.name === '系命'
              resolve(hasDetail && correctKeyword)
            }, 500)
          })
        }
      }
    ]

    // 执行测试
    for (const step of testSteps) {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const startTime = Date.now()
      let result
      
      try {
        result = await step.action()
        const duration = Date.now() - startTime
        
        this.data.testResults.push({
          name: step.name,
          status: result ? 'success' : 'fail',
          duration,
          errorMsg: result ? null : '测试条件未满足'
        })
        
        this.setData({ testResults: this.data.testResults })
      } catch (e) {
        const duration = Date.now() - startTime
        this.data.testResults.push({
          name: step.name,
          status: 'fail',
          duration,
          errorMsg: e.message || '未知错误'
        })
        
        this.setData({ testResults: this.data.testResults })
      }
    }

    this.setData({ autoTesting: false })

    // 显示测试报告
    const successCount = this.data.testResults.filter(r => r.status === 'success').length
    wx.showModal({
      title: '自动化测试完成',
      content: `成功: ${successCount}/${this.data.testResults.length}`,
      showCancel: false
    })
  }
})
