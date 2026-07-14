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
    isLightTheme: true,
    lightOnly: true,
    showAIJudgeCard: false,
    db: db
  },

  version: '1.0.0',

  onLaunch() {
    this.globalData.isLightTheme = true
  },

  onShow() {},

  // P2: 锁定亮色，toggleTheme 改为 noop
  toggleTheme() {
    console.log('[app] P2: 暗色主题已锁定为亮色，P3 阶段开放')
    return true
  },

  updateTheme(isLight) {
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) page.updateTheme(true)
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
