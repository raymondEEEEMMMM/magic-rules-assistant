// pages/apitest/apitest.js
Page({
  data: {
    apiBase: 'https://magic-rules-assistant-0a1904c329.tcb.qcloud.la',
    loading: false,
    passedCount: 0,
    failedCount: 0,
    totalTime: 0,
    testResults: [],
    testId: 0
  },

  onLoad() {
    // 检查是否有缓存的API地址
    const cachedApiBase = wx.getStorageSync('apiBase')
    if (cachedApiBase) {
      this.setData({ apiBase: cachedApiBase })
    }
  },

  onApiInput(e) {
    const apiBase = e.detail.value
    this.setData({ apiBase })
    wx.setStorageSync('apiBase', apiBase)
  },

  // 生成唯一ID
  generateId() {
    this.setData({ testId: this.data.testId + 1 })
    return this.data.testId
  },

  // 添加测试结果
  addTestResult(name, status, time, requestPath, response, statusCode, error) {
    const testResults = [...this.data.testResults, {
      id: this.generateId(),
      name,
      status,
      time,
      requestPath,
      response: response ? JSON.stringify(response).substring(0, 500) : '',
      statusCode,
      error
    }]

    const passedCount = status === 'success' ? this.data.passedCount + 1 : this.data.passedCount
    const failedCount = status === 'fail' ? this.data.failedCount + 1 : this.data.failedCount
    const totalTime = this.data.totalTime + time

    this.setData({
      testResults,
      passedCount,
      failedCount,
      totalTime
    })
  },

  // 执行HTTP请求
  makeRequest(path, data = {}) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      
      wx.request({
        url: `${this.data.apiBase}${path}`,
        data,
        method: 'GET',
        success: (res) => {
          const time = Date.now() - startTime
          resolve({
            statusCode: res.statusCode,
            data: res.data,
            time
          })
        },
        fail: (err) => {
          const time = Date.now() - startTime
          reject({
            error: err.errMsg || '请求失败',
            time
          })
        }
      })
    })
  },

  // 测试1: 健康检查
  async testHealth() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const result = await this.makeRequest('/')
      console.log('健康检查响应:', result)
      const success = result.statusCode === 200 && result.data
      
      this.addTestResult(
        '健康检查',
        success ? 'success' : 'fail',
        result.time,
        '/',
        result.data,
        result.statusCode,
        success ? null : '响应异常'
      )
    } catch (error) {
      console.error('健康检查错误:', error)
      this.addTestResult(
        '健康检查',
        'fail',
        error.time,
        '/',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试2: 规则搜索
  async testSearch() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const result = await this.makeRequest('/api/search', { q: 'combat' })
      console.log('规则搜索响应:', result)
      const success = result.statusCode === 200 && result.data
      
      this.addTestResult(
        '规则搜索',
        success ? 'success' : 'fail',
        result.time,
        '/api/search?q=combat',
        result.data,
        result.statusCode,
        success ? null : '响应数据异常'
      )
    } catch (error) {
      console.error('规则搜索错误:', error)
      this.addTestResult(
        '规则搜索',
        'fail',
        error.time,
        '/api/search?q=combat',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试3: 关键词查询
  async testKeyword() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const result = await this.makeRequest('/api/keyword', { k: 'Lifelink' })
      console.log('关键词查询响应:', result)
      const success = result.statusCode === 200 && result.data
      
      this.addTestResult(
        '关键词查询',
        success ? 'success' : 'fail',
        result.time,
        '/api/keyword?k=Lifelink',
        result.data,
        result.statusCode,
        success ? null : '响应数据异常'
      )
    } catch (error) {
      console.error('关键词查询错误:', error)
      this.addTestResult(
        '关键词查询',
        'fail',
        error.time,
        '/api/keyword?k=Lifelink',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试4: 卡牌搜索
  async testCard() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const result = await this.makeRequest('/api/card', { q: 'Lightning Bolt', page: 1, page_size: 5 })
      console.log('卡牌搜索响应:', result)
      const success = result.statusCode === 200 && result.data && result.data.items

      this.addTestResult(
        '卡牌搜索',
        success ? 'success' : 'fail',
        result.time,
        '/api/card?q=Lightning Bolt',
        result.data,
        result.statusCode,
        success ? null : '响应数据异常'
      )
    } catch (error) {
      console.error('卡牌搜索错误:', error)
      this.addTestResult(
        '卡牌搜索',
        'fail',
        error.time,
        '/api/card?q=Lightning Bolt',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试5: 单张卡牌详情
  async testCardDetail() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      // 先搜索获取一个卡牌ID
      const searchResult = await this.makeRequest('/api/card', { q: 'Lightning Bolt', page: 1, page_size: 1 })
      console.log('搜索响应:', searchResult)

      if (searchResult.statusCode === 200 && searchResult.data && searchResult.data.items && searchResult.data.items.length > 0) {
        const cardId = searchResult.data.items[0].id
        console.log('获取到卡牌ID:', cardId)

        const result = await this.makeRequest('/api/mtgch/card', { id: cardId })
        console.log('卡牌详情响应:', result)
        const success = result.statusCode === 200 && result.data && result.data.name

        this.addTestResult(
          '单张卡牌详情',
          success ? 'success' : 'fail',
          result.time,
          '/api/mtgch/card',
          result.data,
          result.statusCode,
          success ? null : '响应数据异常'
        )
      } else {
        this.addTestResult(
          '单张卡牌详情',
          'fail',
          searchResult.time,
          '/api/mtgch/card',
          null,
          searchResult.statusCode,
          '无法获取测试用卡牌ID'
        )
      }
    } catch (error) {
      console.error('单张卡牌详情错误:', error)
      this.addTestResult(
        '单张卡牌详情',
        'fail',
        error.time,
        '/api/mtgch/card',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试6: 随机卡牌
  async testRandomCard() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const result = await this.makeRequest('/api/mtgch/random')
      console.log('随机卡牌响应:', result)
      const success = result.statusCode === 200 && result.data && result.data.name

      this.addTestResult(
        '随机卡牌',
        success ? 'success' : 'fail',
        result.time,
        '/api/mtgch/random',
        result.data,
        result.statusCode,
        success ? null : '响应数据异常'
      )
    } catch (error) {
      console.error('随机卡牌错误:', error)
      this.addTestResult(
        '随机卡牌',
        'fail',
        error.time,
        '/api/mtgch/random',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试7: 自动补全
  async testAutocomplete() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const result = await this.makeRequest('/api/mtgch/autocomplete', { q: 'light', size: 5 })
      console.log('自动补全响应:', result)
      const success = result.statusCode === 200 && result.data && result.data.suggestions

      this.addTestResult(
        '自动补全',
        success ? 'success' : 'fail',
        result.time,
        '/api/mtgch/autocomplete?q=light',
        result.data,
        result.statusCode,
        success ? null : '响应数据异常'
      )
    } catch (error) {
      console.error('自动补全错误:', error)
      this.addTestResult(
        '自动补全',
        'fail',
        error.time,
        '/api/mtgch/autocomplete?q=light',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试5: 全部测试
  async testAll() {
    if (this.data.loading) return
    this.setData({
      loading: true,
      passedCount: 0,
      failedCount: 0,
      totalTime: 0,
      testResults: []
    })

    const tests = [
      () => this.testHealth(),
      () => this.testSearch(),
      () => this.testKeyword(),
      () => this.testCard(),
      () => this.testCardDetail(),
      () => this.testRandomCard(),
      () => this.testAutocomplete()
    ]

    for (const test of tests) {
      await test()
      // 添加延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    this.setData({ loading: false })

    // 显示总结
    wx.showModal({
      title: '测试完成',
      content: `成功: ${this.data.passedCount}\n失败: ${this.data.failedCount}\n总耗时: ${this.data.totalTime}ms`,
      showCancel: false
    })
  },

  // 清除结果
  clearResults() {
    this.setData({
      passedCount: 0,
      failedCount: 0,
      totalTime: 0,
      testResults: [],
      testId: 0
    })
    wx.showToast({
      title: '已清除',
      icon: 'success'
    })
  }
})
