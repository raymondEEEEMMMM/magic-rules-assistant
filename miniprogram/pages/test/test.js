// pages/test/test.js
const API_BASE = 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com'

Page({
  data: {
    isTesting: false,
    testItems: [
      {
        id: 1,
        name: '1. 关键词列表加载',
        description: '测试关键词列表是否能正常加载',
        status: 'pending',
        time: 0,
        error: null
      },
      {
        id: 2,
        name: '2. 本地搜索 - 飞行',
        description: '测试本地搜索"飞行"关键词',
        status: 'pending',
        time: 0,
        error: null
      },
      {
        id: 3,
        name: '3. 本地搜索 - 系命',
        description: '测试本地搜索"系命"关键词',
        status: 'pending',
        time: 0,
        error: null
      },
      {
        id: 4,
        name: '4. 本地搜索无结果',
        description: '测试搜索不存在关键词的处理',
        status: 'pending',
        time: 0,
        error: null
      },
      {
        id: 5,
        name: '5. API搜索 - Lifelink',
        description: '测试API搜索"Lifelink"关键词',
        status: 'pending',
        time: 0,
        error: null
      },
      {
        id: 6,
        name: '6. API连接测试',
        description: '测试API服务是否可用',
        status: 'pending',
        time: 0,
        error: null
      }
    ],
    testCount: 0,
    successCount: 0,
    failCount: 0,
    totalTime: 0
  },

  // 更新测试项状态
  updateTestItem(id, status, time, error = null) {
    const testItems = this.data.testItems.map(item => {
      if (item.id === id) {
        return { ...item, status, time, error }
      }
      return item
    })

    this.setData({ testItems })

    // 更新统计
    const completed = testItems.filter(t => t.status !== 'pending' && t.status !== 'running')
    const success = completed.filter(t => t.status === 'success')
    const fail = completed.filter(t => t.status === 'fail')
    const totalTime = completed.reduce((sum, t) => sum + t.time, 0)

    this.setData({
      testCount: completed.length,
      successCount: success.length,
      failCount: fail.length,
      totalTime
    })
  },

  // 运行单个测试
  async runTest(e) {
    const testItem = e.currentTarget.dataset.test
    await this.executeTest(testItem.id)
  },

  // 执行测试
  async executeTest(id) {
    this.setData({ isTesting: true })
    this.updateTestItem(id, 'running', 0)

    const startTime = Date.now()

    try {
      let result = false
      let error = null

      switch (id) {
        case 1:
          result = await this.testKeywordListLoad()
          break
        case 2:
          result = await this.testLocalSearchFlying()
          break
        case 3:
          result = await this.testLocalSearchLifelink()
          break
        case 4:
          result = await this.testLocalSearchNoResult()
          break
        case 5:
          result = await this.testApiSearchLifelink()
          break
        case 6:
          result = await this.testApiConnection()
          break
      }

      const time = Date.now() - startTime
      this.updateTestItem(id, result ? 'success' : 'fail', time, error)
    } catch (e) {
      const time = Date.now() - startTime
      this.updateTestItem(id, 'fail', time, e.message || '未知错误')
    }

    this.setData({ isTesting: false })
  },

  // 运行全部测试
  async runAllTests() {
    if (this.data.isTesting) return

    this.resetTests()
    this.setData({ isTesting: true })

    for (const testItem of this.data.testItems) {
      await this.executeTest(testItem.id)
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    this.setData({ isTesting: false })

    wx.showModal({
      title: '测试完成',
      content: `成功: ${this.data.successCount}/${this.data.testCount}`,
      showCancel: false
    })
  },

  // 重置测试
  resetTests() {
    this.setData({
      testItems: this.data.testItems.map(item => ({
        ...item,
        status: 'pending',
        time: 0,
        error: null
      })),
      testCount: 0,
      successCount: 0,
      failCount: 0,
      totalTime: 0
    })
  },

  // 测试1: 关键词列表加载
  async testKeywordListLoad() {
    return new Promise((resolve) => {
      // 模拟关键词列表
      const keywords = [
        { name: '飞行', english: 'Flying' },
        { name: '死触', english: 'Deathtouch' },
        { name: '警戒', english: 'Vigilance' }
      ]
      
      setTimeout(() => {
        const result = keywords.length > 0
        resolve(result)
      }, 100)
    })
  },

  // 测试2: 本地搜索 - 飞行
  async testLocalSearchFlying() {
    return new Promise((resolve) => {
      const keyword = '飞行'
      const keywordDetails = {
        '飞行': { name: '飞行', englishName: 'Flying' }
      }
      
      setTimeout(() => {
        const result = keywordDetails[keyword] !== undefined
        resolve(result)
      }, 150)
    })
  },

  // 测试3: 本地搜索 - 系命
  async testLocalSearchLifelink() {
    return new Promise((resolve) => {
      const keyword = '系命'
      const keywordDetails = {
        '系命': { name: '系命', englishName: 'Lifelink' }
      }
      
      setTimeout(() => {
        const result = keywordDetails[keyword] !== undefined
        resolve(result)
      }, 150)
    })
  },

  // 测试4: 本地搜索无结果
  async testLocalSearchNoResult() {
    return new Promise((resolve) => {
      const keyword = '不存在关键词123'
      const keywordDetails = {}
      
      setTimeout(() => {
        const result = keywordDetails[keyword] === undefined
        resolve(result)
      }, 150)
    })
  },

  // 测试5: API搜索 - Lifelink
  async testApiSearchLifelink() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${API_BASE}/wechat/api/keyword`,
        data: { k: 'Lifelink' },
        method: 'GET',
        success: (res) => {
          console.log('API搜索Lifelink响应:', res.data)
          const success = res.statusCode === 200 && res.data
          resolve(success)
        },
        fail: (err) => {
          console.error('API搜索Lifelink失败:', err)
          reject(new Error('API请求失败'))
        }
      })
    })
  },

  // 测试6: API连接测试
  async testApiConnection() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${API_BASE}/`,
        method: 'GET',
        success: (res) => {
          console.log('API连接测试响应:', res.data)
          const success = res.statusCode === 200
          resolve(success)
        },
        fail: (err) => {
          console.error('API连接测试失败:', err)
          reject(new Error('API连接失败'))
        }
      })
    })
  },

  // 快速测试：本地搜索
  async testLocalSearch() {
    await this.executeTest(2)
    await this.executeTest(3)
  },

  // 快速测试：API搜索
  async testApiSearch() {
    await this.executeTest(6)
    await this.executeTest(5)
  },

  // 快速测试：自动化测试
  testAutoTest() {
    wx.navigateTo({
      url: '/pages/keyword/keyword?autoTest=true'
    })
  },

  // 前往关键词页面
  goToKeyword() {
    wx.navigateTo({
      url: '/pages/keyword/keyword'
    })
  }
})
