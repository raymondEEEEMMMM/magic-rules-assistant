// pages/apitest/apitest.js
const app = getApp()

Page({
  data: {
    // AI 裁判测试
    aiJudgeStatus: 'pending',
    aiJudgeStatusText: '待测试',
    aiJudgeLoading: false,
    aiJudgeResult: '',

    // 规则搜索测试
    ruleSearchStatus: 'pending',
    ruleSearchStatusText: '待测试',
    ruleSearchLoading: false,
    ruleSearchResult: '',

    // 卡牌查询测试
    cardSearchStatus: 'pending',
    cardSearchStatusText: '待测试',
    cardSearchLoading: false,
    cardSearchResult: '',

    // 关键词查询测试
    keywordStatus: 'pending',
    keywordStatusText: '待测试',
    keywordLoading: false,
    keywordResult: ''
  },

  onLoad() {
    // 页面加载
  },

  // 测试 AI 裁判 API
  testAiJudge() {
    this.setData({
      aiJudgeLoading: true,
      aiJudgeStatus: 'pending',
      aiJudgeStatusText: '测试中',
      aiJudgeResult: ''
    })

    wx.request({
      url: `${app.globalData.apiBase}/api/ai-judge/chat`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        message: '你好，请回复"测试成功"',
        session_id: 'apitest'
      },
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            aiJudgeStatus: 'success',
            aiJudgeStatusText: '通过',
            aiJudgeResult: JSON.stringify(res.data, null, 2)
          })
        } else {
          this.setData({
            aiJudgeStatus: 'error',
            aiJudgeStatusText: '失败',
            aiJudgeResult: JSON.stringify(res.data, null, 2)
          })
        }
      },
      fail: (err) => {
        this.setData({
          aiJudgeStatus: 'error',
          aiJudgeStatusText: '失败',
          aiJudgeResult: `网络错误: ${err.errMsg}`
        })
      },
      complete: () => {
        this.setData({
          aiJudgeLoading: false
        })
      }
    })
  },

  // 测试 规则搜索 API
  testRuleSearch() {
    this.setData({
      ruleSearchLoading: true,
      ruleSearchStatus: 'pending',
      ruleSearchStatusText: '测试中',
      ruleSearchResult: ''
    })

    wx.request({
      url: `${app.globalData.apiBase}/api/search`,
      method: 'GET',
      data: {
        q: '战斗'
      },
      success: (res) => {
        if (res.data && res.data.results) {
          this.setData({
            ruleSearchStatus: 'success',
            ruleSearchStatusText: '通过',
            ruleSearchResult: JSON.stringify(res.data, null, 2)
          })
        } else {
          this.setData({
            ruleSearchStatus: 'error',
            ruleSearchStatusText: '失败',
            ruleSearchResult: JSON.stringify(res.data, null, 2)
          })
        }
      },
      fail: (err) => {
        this.setData({
          ruleSearchStatus: 'error',
          ruleSearchStatusText: '失败',
          ruleSearchResult: `网络错误: ${err.errMsg}`
        })
      },
      complete: () => {
        this.setData({
          ruleSearchLoading: false
        })
      }
    })
  },

  // 测试卡牌查询 API
  testCardSearch() {
    this.setData({
      cardSearchLoading: true,
      cardSearchStatus: 'pending',
      cardSearchStatusText: '测试中',
      cardSearchResult: ''
    })

    wx.request({
      url: `${app.globalData.apiBase}/api/card`,
      method: 'GET',
      data: {
        n: '黑莲花'
      },
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            cardSearchStatus: 'success',
            cardSearchStatusText: '通过',
            cardSearchResult: JSON.stringify(res.data, null, 2)
          })
        } else {
          this.setData({
            cardSearchStatus: 'error',
            cardSearchStatusText: '失败',
            cardSearchResult: JSON.stringify(res.data, null, 2)
          })
        }
      },
      fail: (err) => {
        this.setData({
          cardSearchStatus: 'error',
          cardSearchStatusText: '失败',
          cardSearchResult: `网络错误: ${err.errMsg}`
        })
      },
      complete: () => {
        this.setData({
          cardSearchLoading: false
        })
      }
    })
  },

  // 测试关键词查询 API
  testKeyword() {
    this.setData({
      keywordLoading: true,
      keywordStatus: 'pending',
      keywordStatusText: '测试中',
      keywordResult: ''
    })

    wx.request({
      url: `${app.globalData.apiBase}/api/keyword`,
      method: 'GET',
      data: {
        k: '飞行'
      },
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            keywordStatus: 'success',
            keywordStatusText: '通过',
            keywordResult: JSON.stringify(res.data, null, 2)
          })
        } else {
          this.setData({
            keywordStatus: 'error',
            keywordStatusText: '失败',
            keywordResult: JSON.stringify(res.data, null, 2)
          })
        }
      },
      fail: (err) => {
        this.setData({
          keywordStatus: 'error',
          keywordStatusText: '失败',
          keywordResult: `网络错误: ${err.errMsg}`
        })
      },
      complete: () => {
        this.setData({
          keywordLoading: false
        })
      }
    })
  },

  // 复制响应结果
  copyResult(e) {
    const result = e.currentTarget.dataset.result
    wx.setClipboardData({
      data: result,
      success: () => {
        wx.showToast({
          title: '已复制',
          icon: 'success'
        })
      }
    })
  }
})
