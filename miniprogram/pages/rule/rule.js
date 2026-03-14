/**
 * 万智牌规则页面逻辑
 */
const app = getApp()
const API_BASE = 'https://magic-rules-assistant-0a1904c329.tcb.qcloud.la'

Page({
  data: {
    activeCategory: 'basic',
    loading: false,
    currentRules: [],
    useApi: false, // 是否使用API
    searchResults: [], // API搜索结果
    allRules: {
      basic: [
        {
          id: 1,
          title: '卡牌类型',
          content: '万智牌卡牌有多种类型，包括：生物、神器、结界、瞬间、法术、鹏洛客、佩带、战场、地、部族和基本地类型。每种类型都有其特殊的规则和用途。',
          example: '生物可以在战斗中攻击和阻挡，神器结界通常永久留在场上，法术和瞬间则是一过性效果。',
          expanded: false
        },
        {
          id: 2,
          title: '颜色',
          content: '万智牌有五种颜色：白、蓝、黑、红、绿。每种颜色有其独特的游戏风格和主题。无色也是卡牌的一种属性。',
          example: '白色代表秩序和治疗，蓝色代表智慧和操控，黑色代表死亡和牺牲，红色代表破坏和速度，绿色代表生长和自然。',
          expanded: false
        },
        {
          id: 3,
          title: '法术力',
          content: '法术力是施放咒语和启动异能的货币。通过使用地牌产生法术力，每张卡牌的右上角显示了其法术力费用。',
          example: '一张费用为"2UU"的卡牌需要支付2点任意法术力和2点蓝色法术力。',
          expanded: false
        },
        {
          id: 4,
          title: '战场',
          content: '战场是永久物所在的地方，包括生物、神器、结界、鹏洛客和地。战场上的永久物持续影响游戏。',
          example: '你可以将一张地放进战场，每个回合最多一张。生物和神器等其他永久物需要通过咒语放入战场。',
          expanded: false
        }
      ],
      turn: [
        {
          id: 5,
          title: '回合阶段',
          content: '每个回合分为多个阶段：开始阶段、准备阶段、抽牌阶段、主阶段、战斗阶段、第二主阶段和结束阶段。',
          example: '在抽牌阶段，你从牌库顶端抽一张牌。在主阶段，你可以施放咒语和启动异能。',
          expanded: false
        },
        {
          id: 6,
          title: '战斗阶段',
          content: '战斗阶段包括开始战斗步骤、宣告攻击者步骤、宣告阻挡者步骤、战斗伤害步骤和结束战斗步骤。',
          example: '你可以用你的生物攻击对手，对手可以选择用他们的生物来阻挡。',
          expanded: false
        },
        {
          id: 7,
          title: '堆叠',
          content: '堆叠是处理咒语和异能的地方。玩家将咒语和异能放入堆叠，最后一个放入的最先结算。',
          example: '当你施放一个瞬间时，对手可以用他们的瞬间回应。所有咒语和异能都会按相反顺序结算。',
          expanded: false
        }
      ],
      keywords: [
        {
          id: 8,
          title: '飞行',
          content: '具有飞行的生物只能被其他具有飞行或延势的生物阻挡。',
          example: '一只具有飞行的生物可以攻击而不被没有飞行或延势的生物阻挡。',
          expanded: false
        },
        {
          id: 9,
          title: '先攻',
          content: '具有先攻的生物在战斗伤害步骤中先于没有先攻的生物造成战斗伤害。具有双重的生物先于没有先攻和具有先攻的生物造成战斗伤害，再于没有先攻和具有先攻的生物造成战斗伤害。',
          example: '如果你的生物具有先攻，它在战斗中先造成伤害，可能会在对手的生物造成伤害前消灭它们。',
          expanded: false
        },
        {
          id: 10,
          title: '系命',
          content: '具有系命的生物在造成战斗伤害时，其操控者获得等量的生命。',
          example: '如果你的3/3生物具有系命并造成3点战斗伤害，你获得3点生命。',
          expanded: false
        },
        {
          id: 11,
          title: '践踏',
          content: '当具有践踏的生物在造成战斗伤害时，若其力量大于阻挡生物的防御力，超出的伤害会分配给受击牌手或鹏洛客。',
          example: '一只5/5践踏生物被2/2生物阻挡，它对阻挡者造成2点伤害，对对手造成3点伤害。',
          expanded: false
        }
      ],
      priority: [
        {
          id: 12,
          title: '优先权',
          content: '优先权是玩家获得施放咒语或启动异能的机会。当玩家获得优先权时，他们可以选择施放咒语、启动异能或让过优先权。',
          example: '在主阶段开始时，你获得优先权。你可以施放一个法术，然后让过优先权给对手。',
          expanded: false
        },
        {
          id: 13,
          title: '堆叠为空时的规则',
          content: '当堆叠为空且所有玩家连续让过优先权时，当前步骤或阶段结束，游戏进入下一个步骤或阶段。',
          example: '如果你施放一个法术，对手响应一个瞬间，你们都让过优先权，堆叠上的咒语和异能按相反顺序结算，然后该阶段结束。',
          expanded: false
        },
        {
          id: 14,
          title: '瞬间时机',
          content: '瞬间可以在你获得优先权的几乎任何时候施放，包括在对手的回合中。',
          example: '当对手攻击时，你可以在宣告阻挡者步骤施放一个瞬间来消灭他们的生物。',
          expanded: false
        }
      ]
    }
  },

  onLoad(options) {
    if (options.query) {
      // 从搜索跳转过来，使用API搜索
      this.setData({ useApi: true })
      this.searchFromApi(options.query)
    } else {
      this.loadRules()
    }
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

  // API搜索规则
  searchFromApi(keyword) {
    wx.showLoading({ title: '搜索中...' })

    wx.request({
      url: `${API_BASE}/api/search`,
      data: { q: keyword },
      method: 'GET',
      success: (res) => {
        wx.hideLoading()
        console.log('规则搜索API响应:', res.data)

        const apiData = res.data

        // 检查错误响应
        if (apiData && apiData.error) {
          wx.showToast({
            title: apiData.error,
            icon: 'none'
          })
          return
        }

        // 正常响应：{ query, count, results: { rules: [...] } }
        if (apiData && apiData.results && apiData.results.rules) {
          const rules = apiData.results.rules.map((rule, index) => ({
            id: Date.now() + index,
            title: rule.rule_number || rule.rule_title || '规则',
            content: rule.rule_content || '无内容',
            example: '',
            expanded: false,
            category: rule.category
          }))

          this.setData({
            currentRules: rules,
            activeCategory: 'search'
          })

          wx.showToast({
            title: `找到 ${rules.length} 条规则`,
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: '未找到相关规则',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('规则搜索API错误:', err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
      }
    })
  },

  /**
   * 加载规则
   */
  loadRules() {
    this.setData({
      loading: true
    })

    // 模拟加载延迟
    setTimeout(() => {
      this.setData({
        currentRules: this.data.allRules[this.data.activeCategory],
        loading: false
      })
    }, 300)
  },

  /**
   * 切换规则分类
   */
  switchCategory(e) {
    const category = e.currentTarget.dataset.category
    if (category === this.data.activeCategory) {
      return
    }

    this.setData({
      activeCategory: category,
      currentRules: this.data.allRules[category]
    })
  },

  /**
   * 展开/收起规则详情
   */
  toggleRule(e) {
    const id = e.currentTarget.dataset.id
    const rules = this.data.currentRules.map(rule => {
      if (rule.id === id) {
        return { ...rule, expanded: !rule.expanded }
      }
      return rule
    })

    this.setData({
      currentRules: rules
    })
  }
})
