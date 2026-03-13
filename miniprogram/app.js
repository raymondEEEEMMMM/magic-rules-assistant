/**
 * 万智牌规则助手 - 小程序入口
 */

// 云开发配置
wx.cloud.init({
  env: 'magic-rules-assistant-0a1904c329', // 替换为您的云环境ID
  traceUser: true
})

App({
  globalData: {
    // API 基础地址
    apiBase: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com',
    userInfo: null
  },

  onLaunch() {
    // 检查登录状态
    this.checkLogin()
  },

  checkLogin() {
    // 获取用户信息
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: res => {
              this.globalData.userInfo = res.userInfo
            }
          })
        }
      }
    })
  },

  // API 请求封装
  requestApi(endpoint, data = {}, method = 'GET') {
    const url = `${this.globalData.apiBase}${endpoint}`
    return new Promise((resolve, reject) => {
      wx.request({
        url,
        method,
        data,
        success: res => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error(`请求失败: ${res.statusCode}`))
          }
        },
        fail: reject
      })
    })
  }
})
