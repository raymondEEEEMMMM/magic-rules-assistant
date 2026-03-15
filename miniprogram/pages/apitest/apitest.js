// pages/apitest/apitest.js
const app = getApp()

Page({
  data: {
    useCloudCall: true,  // 使用云调用
    loading: false,
    passedCount: 0,
    failedCount: 0,
    totalTime: 0,
    testResults: [],
    testId: 0
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

  // 调用云函数
  callCloudFunction(path, query = {}) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now()

      wx.cloud.callFunction({
        name: 'mtgAsk',
        data: {
          httpMethod: 'GET',
          path: path,
          queryString: Object.entries(query).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&')
        },
        success: (res) => {
          const time = Date.now() - startTime
          let data = null
          let statusCode = 0

          if (res.result) {
            if (res.result.body) {
              try {
                data = typeof res.result.body === 'string' ? JSON.parse(res.result.body) : res.result.body
              } catch (e) {
                data = res.result.body
              }
            } else {
              data = res.result
            }
            statusCode = res.result.statusCode || 200
          }

          resolve({
            statusCode,
            data,
            time
          })
        },
        fail: (err) => {
          const time = Date.now() - startTime
          reject({
            error: err.errMsg || '调用失败',
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
      const result = await this.callCloudFunction('/')
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
      const result = await this.callCloudFunction('/api/search', { q: 'flying' })
      console.log('规则搜索响应:', result)
      const success = result.statusCode === 200 && result.data

      this.addTestResult(
        '规则搜索',
        success ? 'success' : 'fail',
        result.time,
        '/api/search?q=flying',
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
        '/api/search?q=flying',
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
      const result = await this.callCloudFunction('/api/keyword', { k: 'Trample' })
      console.log('关键词查询响应:', result)
      const success = result.statusCode === 200 && result.data

      this.addTestResult(
        '关键词查询',
        success ? 'success' : 'fail',
        result.time,
        '/api/keyword?k=Trample',
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
        '/api/keyword?k=Trample',
        null,
        null,
        error.error
      )
    }

    this.setData({ loading: false })
  },

  // 测试4: 全部测试
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
      () => this.testKeyword()
    ]

    for (const test of tests) {
      await test()
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    this.setData({ loading: false })

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
