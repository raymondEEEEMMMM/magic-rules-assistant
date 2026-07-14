/**
 * HTTP 封装（云函数调用）
 *
 * 用法:
 *   const http = require('./utils/http.js')
 *   const data = await http.requestCloud('/api/search', { q: '飞行' })
 */

const FUNCTION_NAME = 'mtgAsk'

function buildQueryString(params) {
  const parts = []
  for (const key in params) {
    if (params[key] !== undefined && params[key] !== null) {
      parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(params[key]))
    }
  }
  return parts.join('&')
}

function buildCloudCallData(path, params, method) {
  const normalizedPath = path.startsWith('/') ? path : '/' + path
  if (method === 'GET') {
    return {
      httpMethod: 'GET',
      path: normalizedPath,
      queryString: buildQueryString(params || {})
    }
  }
  return {
    httpMethod: method,
    path: normalizedPath,
    body: JSON.stringify(params || {})
  }
}

function parseResponse(res) {
  let result = res.result
  if (!result) return null

  if (result.body) {
    try {
      result = typeof result.body === 'string' ? JSON.parse(result.body) : result.body
    } catch (e) {
      console.warn('[http.parseResponse] body parse failed', e)
    }
  }
  if (typeof result === 'string') {
    try {
      result = JSON.parse(result)
    } catch (e) {
      // 保持字符串
    }
  }
  return result
}

function requestCloud(path, params, opts) {
  opts = opts || {}
  const method = opts.method || 'GET'
  const showLoading = opts.showLoading === true

  return new Promise(function(resolve, reject) {
    if (showLoading) {
      wx.showLoading({ title: '加载中...' })
    }

    const callData = buildCloudCallData(path, params, method)

    wx.cloud.callFunction({
      name: FUNCTION_NAME,
      data: callData,
      success: function(res) {
        if (showLoading) wx.hideLoading()
        if (res.errMsg && res.errMsg.includes('fail')) {
          reject(new Error(res.errMsg))
          return
        }
        const result = parseResponse(res)
        if (result && result.error) {
          reject(new Error(result.error))
          return
        }
        resolve(result)
      },
      fail: function(err) {
        if (showLoading) wx.hideLoading()
        reject(err)
      }
    })
  })
}

function get(path, params, opts) {
  return requestCloud(path, params, Object.assign({}, opts, { method: 'GET' }))
}

function post(path, params, opts) {
  return requestCloud(path, params, Object.assign({}, opts, { method: 'POST' }))
}

module.exports = {
  requestCloud: requestCloud,
  get: get,
  post: post,
  buildQueryString: buildQueryString,
  buildCloudCallData: buildCloudCallData,
  parseResponse: parseResponse
}