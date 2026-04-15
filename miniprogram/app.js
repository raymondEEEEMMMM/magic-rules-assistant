/**
 * mtgAsk - 小程序入口
 */

// 云开发配置
wx.cloud.init({
  env: 'magic-rules-assistant-0a1904c329',
  traceUser: true
})

// 云数据库
const db = wx.cloud.database()

App({
  globalData: {
    // 云函数名称
    functionName: 'mtgAsk',
    userInfo: null,
    isLightTheme: false,
    showAIJudgeCard: false,
    db
  },

  // 小程序版本号
  version: '1.0.0',

  onLaunch() {
    console.log('CODEBUDDY_DEBUG app onLaunch started')
    // 读取主题设置，默认日间主题
    const theme = wx.getStorageSync('appTheme') || 'light'
    this.globalData.isLightTheme = theme === 'light'
    console.log('CODEBUDDY_DEBUG app theme loaded theme=', theme, 'isLightTheme=', this.globalData.isLightTheme)
    this.updateTheme(theme === 'light')
    console.log('CODEBUDDY_DEBUG app onLaunch completed')
  },

  onShow() {
    console.log('CODEBUDDY_DEBUG app onShow')
  },

  // 切换主题
  toggleTheme() {
    const newTheme = !this.globalData.isLightTheme
    this.globalData.isLightTheme = newTheme
    wx.setStorageSync('appTheme', newTheme ? 'light' : 'dark')
    this.updateTheme(newTheme)
    return newTheme
  },

  // 更新页面主题
  updateTheme(isLight) {
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) {
        page.updateTheme(isLight)
      }
    })
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
