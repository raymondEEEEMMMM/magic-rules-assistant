/**
 * 存储封装
 *
 * 统一命名空间（默认 'app'），避免 key 冲突。
 * 用法:
 *   storage.set('theme', 'dark')
 *   storage.get('theme', 'light')
 *   storage.remove('theme')
 *   storage.set('list', [], 'search')
 */

const DEFAULT_NS = 'app'

function namespacedKey(key, namespace) {
  return (namespace || DEFAULT_NS) + ':' + key
}

module.exports = {
  set(key, value, namespace) {
    try {
      wx.setStorageSync(namespacedKey(key, namespace), JSON.stringify(value))
    } catch (e) {
      console.warn('[storage.set] failed', e)
    }
  },

  get(key, defaultValue, namespace) {
    try {
      const raw = wx.getStorageSync(namespacedKey(key, namespace))
      if (raw === '' || raw === undefined || raw === null) {
        return defaultValue
      }
      return JSON.parse(raw)
    } catch (e) {
      console.warn('[storage.get] failed', e)
      return defaultValue
    }
  },

  remove(key, namespace) {
    try {
      wx.removeStorageSync(namespacedKey(key, namespace))
    } catch (e) {
      console.warn('[storage.remove] failed', e)
    }
  },

  clearNamespace(namespace) {
    console.warn('[storage.clearNamespace] not implemented for wx')
  }
}
