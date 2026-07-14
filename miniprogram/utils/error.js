/**
 * 错误处理
 *
 * 用法:
 *   const errorUtil = require('./utils/error.js')
 *   errorUtil.handle(err, { context: '搜索失败' })
 */

const TYPE_NETWORK = 'network'
const TYPE_TIMEOUT = 'timeout'
const TYPE_BUSINESS = 'business'
const TYPE_AUTH = 'auth'
const TYPE_SERVER = 'server'
const TYPE_UNKNOWN = 'unknown'

const FRIENDLY_MESSAGES = {
  [TYPE_NETWORK]: '网络连接失败，请检查网络',
  [TYPE_TIMEOUT]: '请求超时，请稍后再试',
  [TYPE_BUSINESS]: null,
  [TYPE_AUTH]: '请登录后重试',
  [TYPE_SERVER]: '服务暂不可用，请稍后再试',
  [TYPE_UNKNOWN]: '操作失败，请稍后重试'
}

function classify(err) {
  if (!err) return TYPE_UNKNOWN

  const msg = (err.errMsg || err.message || String(err)).toLowerCase()

  if (msg.includes('timeout') || msg.includes('timed out') || msg.includes('time_limit')) {
    return TYPE_TIMEOUT
  }
  if (msg.includes('fail') && !msg.includes('timeout')) {
    return TYPE_NETWORK
  }
  if (err.statusCode === 401 || err.statusCode === 403) {
    return TYPE_AUTH
  }
  if (err.statusCode >= 500) {
    return TYPE_SERVER
  }
  return TYPE_BUSINESS
}

function friendlyMessage(err) {
  const type = classify(err)
  if (type === TYPE_BUSINESS) {
    return err.message || err.errMsg || FRIENDLY_MESSAGES[TYPE_UNKNOWN]
  }
  return FRIENDLY_MESSAGES[type] || FRIENDLY_MESSAGES[TYPE_UNKNOWN]
}

function handle(err, opts) {
  opts = opts || {}
  const context = opts.context || ''
  const silent = opts.silent === true
  const message = friendlyMessage(err)

  if (!silent) {
    wx.showToast({ title: message, icon: 'none', duration: 2000 })
  }

  if (context) {
    console.warn('[error] ' + context + ':', err)
  }

  return { type: classify(err), message: message }
}

module.exports = {
  classify: classify,
  friendlyMessage: friendlyMessage,
  handle: handle,
  TYPES: {
    NETWORK: TYPE_NETWORK,
    TIMEOUT: TYPE_TIMEOUT,
    BUSINESS: TYPE_BUSINESS,
    AUTH: TYPE_AUTH,
    SERVER: TYPE_SERVER,
    UNKNOWN: TYPE_UNKNOWN
  }
}