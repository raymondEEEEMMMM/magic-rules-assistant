/**
 * mtgAsk - 小程序入口
 */

const themeUtil = require('./utils/theme.js')

wx.cloud.init({
  env: 'magic-rules-assistant-0a1904c329',
  traceUser: true
})

const db = wx.cloud.database()

App({
  globalData: {
    functionName: 'mtgAsk',
    userInfo: null,
    isLightTheme: themeUtil.isLight(),
    lightOnly: false,
    showAIJudgeCard: false,
    db: db
  },

  version: '1.0.0',

  onLaunch() {
    this.globalData.isLightTheme = themeUtil.isLight()
  },

  onShow() {},

  // P3: 启用主题切换
  toggleTheme() {
    return themeUtil.toggle()
  },

  updateTheme(isLight) {
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) page.updateTheme(isLight)
    })
  },

  checkLogin() {
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: res => { this.globalData.userInfo = res.userInfo }
          })
        }
      }
    })
  }
})
