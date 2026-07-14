/**
 * utils 单元测试
 * 运行: 在 minitest 页面点击"运行测试"
 */

const storage = require('../utils/storage.js')

// ============= storage =============
function test_storage_set_and_get() {
  storage.set('test:key', { foo: 'bar' })
  const got = storage.get('test:key')
  if (JSON.stringify(got) !== JSON.stringify({ foo: 'bar' })) {
    throw new Error('expected {foo:bar}, got ' + JSON.stringify(got))
  }
}

function test_storage_get_with_default() {
  const got = storage.get('test:nonexistent', 'default-value')
  if (got !== 'default-value') {
    throw new Error('expected default-value, got ' + got)
  }
}

function test_storage_remove() {
  storage.set('test:to-remove', 'value')
  storage.remove('test:to-remove')
  const got = storage.get('test:to-remove')
  if (got !== undefined) {
    throw new Error('expected undefined, got ' + got)
  }
}

function test_storage_namespacing() {
  storage.set('a:key', 1, 'ns1')
  storage.set('a:key', 2, 'ns2')
  if (storage.get('a:key', null, 'ns1') !== 1) throw new Error('ns1 wrong')
  if (storage.get('a:key', null, 'ns2') !== 2) throw new Error('ns2 wrong')
}

const theme = require('../utils/theme.js')

function test_theme_default_is_light() {
  const result = theme.getCurrent()
  if (result !== 'light') {
    throw new Error('expected light, got ' + result)
  }
}

function test_theme_isLight() {
  theme.set('dark')
  if (theme.isLight() !== false) throw new Error('isLight should be false when dark')
  theme.set('light')
  if (theme.isLight() !== true) throw new Error('isLight should be true when light')
}

function test_theme_toggle() {
  theme.set('light')
  const after1 = theme.toggle()
  if (after1 !== 'dark') throw new Error('toggle from light should give dark')
  const after2 = theme.toggle()
  if (after2 !== 'light') throw new Error('toggle from dark should give light')
}

const errorUtil = require('../utils/error.js')

function test_error_classify_network() {
  const err = { errMsg: 'request:fail' }
  const type = errorUtil.classify(err)
  if (type !== 'network') throw new Error('expected network, got ' + type)
}

function test_error_classify_timeout() {
  const err = { errMsg: 'request:fail timeout' }
  const type = errorUtil.classify(err)
  if (type !== 'timeout') throw new Error('expected timeout, got ' + type)
}

function test_error_classify_business() {
  const err = '业务错误：参数无效'
  const type = errorUtil.classify(err)
  if (type !== 'business') throw new Error('expected business, got ' + type)
}

function test_error_friendlyMessage_network() {
  const msg = errorUtil.friendlyMessage({ errMsg: 'request:fail' })
  if (!msg.includes('网络')) throw new Error('expected 网络提示, got: ' + msg)
}

function test_error_handle_with_toast() {
  let toastCalled = null
  const origToast = wx.showToast
  wx.showToast = (opts) => { toastCalled = opts }
  errorUtil.handle({ errMsg: 'request:fail' }, { silent: false, context: '测试场景' })
  wx.showToast = origToast
  if (!toastCalled || !toastCalled.title.includes('网络')) {
    throw new Error('Toast should be called with network message')
  }
}

function test_error_handle_silent() {
  let toastCalled = false
  const origToast = wx.showToast
  wx.showToast = () => { toastCalled = true }
  errorUtil.handle({ errMsg: 'request:fail' }, { silent: true })
  wx.showToast = origToast
  if (toastCalled) throw new Error('Toast should not be called in silent mode')
}

module.exports = {
  'storage.set+get': test_storage_set_and_get,
  'storage.get default': test_storage_get_with_default,
  'storage.remove': test_storage_remove,
  'storage.namespace': test_storage_namespacing,
  'theme default light': test_theme_default_is_light,
  'theme isLight': test_theme_isLight,
  'theme toggle': test_theme_toggle,
  'error classify network': test_error_classify_network,
  'error classify timeout': test_error_classify_timeout,
  'error classify business': test_error_classify_business,
  'error friendlyMessage network': test_error_friendlyMessage_network,
  'error handle toast': test_error_handle_with_toast,
  'error handle silent': test_error_handle_silent
}
