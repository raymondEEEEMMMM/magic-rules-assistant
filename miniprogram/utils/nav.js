/**
 * 导航封装
 *
 * 用法:
 *   nav.navigateTo('/pages/card/card', { id: 'xxx' })
 *   nav.redirectTo('/pages/login/login')
 *   nav.switchTab('/pages/index/index')
 *   nav.goBack()
 */

function buildUrl(path, query) {
  if (!query || Object.keys(query).length === 0) return path
  const parts = []
  for (const key in query) {
    if (query[key] !== undefined && query[key] !== null) {
      parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(query[key]))
    }
  }
  return path + '?' + parts.join('&')
}

function navigateTo(path, query) {
  return new Promise(function(resolve, reject) {
    wx.navigateTo({
      url: buildUrl(path, query),
      success: resolve,
      fail: reject
    })
  })
}

function redirectTo(path, query) {
  return new Promise(function(resolve, reject) {
    wx.redirectTo({
      url: buildUrl(path, query),
      success: resolve,
      fail: reject
    })
  })
}

function switchTab(path) {
  return new Promise(function(resolve, reject) {
    wx.switchTab({
      url: path,
      success: resolve,
      fail: reject
    })
  })
}

function goBack(delta) {
  delta = delta || 1
  return new Promise(function(resolve) {
    wx.navigateBack({ delta: delta, success: resolve, fail: resolve })
  })
}

module.exports = {
  buildUrl: buildUrl,
  navigateTo: navigateTo,
  redirectTo: redirectTo,
  switchTab: switchTab,
  goBack: goBack
}
