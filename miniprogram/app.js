/**
 * mtgAsk - 小程序入口
 */

// 云开发配置
wx.cloud.init({
  env: 'magic-rules-assistant-0a1904c329',
  traceUser: true
})

App({
  globalData: {
    // 云函数名称
    functionName: 'mtgAsk',
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
  }
})
