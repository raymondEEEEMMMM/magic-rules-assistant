/**
 * 主题管理
 *
 * 用法:
 *   theme.getCurrent()  // 'light' | 'dark'
 *   theme.isLight()
 *   theme.set('dark')
 *   theme.toggle()
 *   theme.applyToPage(page)
 */

const storage = require('./storage.js')

const KEY = 'theme'

module.exports = {
  getCurrent() {
    return storage.get(KEY, 'light')
  },

  isLight() {
    return this.getCurrent() === 'light'
  },

  set(themeName) {
    storage.set(KEY, themeName)
    this._applyToAllPages()
  },

  toggle() {
    const next = this.isLight() ? 'dark' : 'light'
    this.set(next)
    return next
  },

  toggleTheme() {
    return this.toggle()
  },

  applyToPage(page) {
    if (!page || !page.setData) return
    page.setData({ isLightTheme: this.isLight() })
  },

  _applyToAllPages() {
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) {
        page.updateTheme(this.isLight())
      }
    })
  }
}
