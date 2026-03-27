/**
 * mtgAsk API 工具
 *
 * 使用方法:
 * const api = require('../../utils/api.js')
 *
 * // 搜索规则
 * api.searchRules('combat').then(data => { ... })
 *
 * // 查询关键词
 * api.getKeyword('Flying').then(data => { ... })
 *
 * // 搜索卡牌
 * api.searchCard('Lightning Bolt').then(data => { ... })
 */

const FUNCTION_NAME = 'mtgAsk'

/**
 * API 封装对象
 */
const api = {
  /**
   * 搜索规则
   * @param {string} keyword - 搜索关键词
   * @returns {Promise}
   */
  searchRules(keyword) {
    if (!keyword || !keyword.trim()) {
      return Promise.reject('请输入搜索关键词')
    }
    return this.request('/api/search', { q: keyword })
  },

  /**
   * 查询关键词
   * @param {string} keyword - 关键词名称（如 Flying, Reach）
   * @returns {Promise}
   */
  getKeyword(keyword) {
    if (!keyword || !keyword.trim()) {
      return Promise.reject('请输入关键词')
    }
    return this.request('/api/keyword', { k: keyword })
  },

  /**
   * 获取规则详情
   * @param {string} ruleNumber - 规则编号（如 702.9）
   * @returns {Promise}
   */
  getRule(ruleNumber) {
    if (!ruleNumber || !ruleNumber.trim()) {
      return Promise.reject('请输入规则编号')
    }
    return this.request('/api/rule', { n: ruleNumber })
  },

  /**
   * 搜索卡牌
   * @param {string} cardName - 卡牌名称
   * @param {number} page - 页码（默认 1）
   * @param {number} pageSize - 每页数量（默认 5）
   * @returns {Promise}
   */
  searchCard(cardName, page = 1, pageSize = 5) {
    if (!cardName || !cardName.trim()) {
      return Promise.reject('请输入卡牌名称')
    }
    return this.request('/api/card', {
      q: cardName,
      page,
      page_size: pageSize
    })
  },

  /**
   * 获取服务状态
   * @returns {Promise}
   */
  getStatus() {
    return this.request('/', {})
  },

  /**
   * 获取单张卡牌详情
   * @param {string} cardId - 卡牌 UUID
   * @returns {Promise}
   */
  getCardById(cardId) {
    if (!cardId) {
      return Promise.reject('请输入卡牌ID')
    }
    return this.request('/api/mtgch/card', { id: cardId })
  },

  /**
   * 通过系列代码和编号获取卡牌
   * @param {string} setCode - 系列代码（如 M19）
   * @param {string} number - 收集编号
   * @returns {Promise}
   */
  getCardBySetAndNumber(setCode, number) {
    if (!setCode || !number) {
      return Promise.reject('请输入系列代码和编号')
    }
    return this.request('/api/mtgch/card', { set: setCode, number })
  },

  /**
   * 获取卡牌官方裁定（通过 Scryfall API）
   * @param {string} cardId - MTGCH 卡牌 UUID（也是 Scryfall card ID）
   * @returns {Promise}
   */
  getCardRulings(cardId) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `https://api.scryfall.com/cards/${cardId}/rulings`,
        success: res => {
          const rulings = res.data?.data || []
          resolve(rulings)
        },
        fail: () => resolve([])
      })
    })
  },

  /**
   * 自动补全
   * @param {string} query - 搜索前缀
   * @param {number} size - 返回数量（默认 10）
   * @returns {Promise}
   */
  autocomplete(query, size = 10) {
    if (!query || !query.trim()) {
      return Promise.reject('请输入搜索内容')
    }
    return this.request('/api/mtgch/autocomplete', { q: query, size })
  },

  // ==================== AI 裁判 API ====================

  /**
   * AI 裁判问答
   * @param {string} message - 用户问题
   * @param {string} sessionId - 会话 ID（可选）
   * @param {string} openid - 用户 openid（可选，用于 per-user agent 隔离）
   * @returns {Promise}
   */

  /**
   * 预热 AI Agent
   * @param {string} openid - 用户 openid（必填）
   * @returns {Promise}
   */
  aiJudgeInit(openid) {
    if (!openid) {
      return Promise.reject('openid 参数必填')
    }
    return this.request('/api/ai-judge/init', { openid }, { method: 'POST' })
  },

  aiJudgeChat(message, sessionId = 'miniprogram', openid = null) {
    if (!message || !message.trim()) {
      return Promise.reject('请输入问题')
    }
    const data = {
      message,
      session_id: sessionId
    }
    // 如果提供了 openid，添加到请求中
    if (openid) {
      data.openid = openid
    }
    return this.request('/api/ai-judge/chat', data, { method: 'POST', showLoading: false })
  },

  /**
   * 清除 AI 裁判会话
   * @param {string} sessionId - 会话 ID（可选）
   * @param {string} openid - 用户 openid（必填）
   * @returns {Promise}
   */
  aiJudgeClear(sessionId = 'miniprogram', openid) {
    return this.request('/api/ai-judge/clear', {
      session_id: sessionId,
      openid: openid
    }, { method: 'POST' })
  },

  /**
   * 获取 AI 裁判会话历史
   * @param {string} openid - 用户 openid（必填）
   * @param {string} sessionId - 会话 ID（可选，不传则返回会话列表）
   * @param {number} limit - 返回数量（默认 10）
   * @param {number} offset - 偏移量（默认 0）
   * @returns {Promise}
   */
  aiJudgeHistory(openid, sessionId = null, limit = 10, offset = 0) {
    if (!openid) {
      return Promise.reject('openid 参数必填')
    }
    const data = {
      openid,
      limit,
      offset
    }
    if (sessionId) {
      data.session_id = sessionId
    }
    return this.request('/api/ai-judge/history', data, { method: 'POST' })
  },

  /**
   * 清理 OpenCLAW 会话（清理过期会话历史）
   * @returns {Promise}
   */
  cleanupSessions() {
    return this.request('/api/admin/cleanup-sessions', {}, { method: 'POST' })
  },

  /**
   * 提交反馈
   * @param {string} content - 反馈内容
   * @param {string} type - 反馈类型：suggestion/bug/other
   * @param {string} openid - 用户 openid（必填）
   * @returns {Promise}
   */
  submitFeedback(content, type = 'suggestion', openid = '') {
    return this.request('/api/feedback', {
      content,
      type,
      openid
    }, { method: 'POST' })
  },

  /**
   * 获取 Agent 池统计信息
   * @returns {Promise}
   */
  getAgentPoolStats() {
    return this.request('/api/admin/agent-pool/stats', {}, { method: 'POST' })
  },

  /**
   * 通用请求方法 - 使用 wx.cloud.callFunction
   * @param {string} path - 请求路径
   * @param {object} data - 请求数据
   * @param {object} options - 额外配置
   * @returns {Promise}
   */
  request(path, data = {}, options = {}) {
    const { method = 'GET', showLoading = true } = options

    return new Promise((resolve, reject) => {
      if (showLoading) {
        wx.showLoading({ title: '加载中...' })
      }

      // 构建调用参数
      const callData = {
        httpMethod: method,
        path: path,
        ...data
      }

      // GET 请求用 queryString，POST 请求用 body
      if (method === 'GET') {
        // 将 data 转为 queryString 格式
        const queryParts = []
        for (const key in data) {
          if (data[key] !== undefined && data[key] !== null) {
            queryParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
          }
        }
        callData.queryString = queryParts.join('&')
        delete callData.path
        callData.path = path.startsWith('/') ? path : '/' + path
      } else {
        // POST 请求
        callData.body = JSON.stringify(data)
        delete callData.path
        callData.path = path.startsWith('/') ? path : '/' + path
      }

      console.log('CODEBUDDY_DEBUG api request started path=', path, 'method=', method, 'data=', data)

      wx.cloud.callFunction({
        name: FUNCTION_NAME,
        data: callData,
        success: res => {
          console.log('CODEBUDDY_DEBUG api request success path=', path, 'res=', JSON.stringify(res).substring(0, 200))
          if (showLoading) {
            wx.hideLoading()
          }

          // 解析云函数返回的结果
          if (res.errMsg && res.errMsg.includes('fail')) {
            reject(`请求失败: ${res.errMsg}`)
            return
          }

          // 云函数返回的是 { statusCode, headers, body } 或直接是数据
          let result = res.result
          if (result) {
            // 如果有 body 字段，解析它
            if (result.body) {
              try {
                result = typeof result.body === 'string' ? JSON.parse(result.body) : result.body
              } catch (e) {
                console.error('解析响应失败:', e)
              }
            }
            // 如果 result 仍然是字符串，尝试解析
            if (typeof result === 'string') {
              try {
                result = JSON.parse(result)
              } catch (e) {
                // 解析失败，保持原值
              }
            }
          }

          if (result && result.error) {
            reject(result.error)
            return
          }

          resolve(result)
        },
        fail: err => {
          console.log('CODEBUDDY_DEBUG api request failed path=', path, 'err=', err)
          if (showLoading) {
            wx.hideLoading()
          }

          console.error('云函数调用失败:', err)
          console.log('CODEBUDDY_DEBUG fail callback err=', JSON.stringify(err).substring(0, 300))

          // 判断错误类型
          if (err.errMsg && (err.errMsg.includes('timeout') || err.errMsg.includes('timed out') || err.errMsg.includes('TIME_LIMIT'))) {
            // chat 接口超时说明是 AI 处理中，让用户刷新
            if (path === '/api/ai-judge/chat') {
              reject('async_timeout')
            } else {
              reject('请求超时，请检查网络')
            }
          } else if (err.errMsg && err.errMsg.includes('fail')) {
            reject('网络连接失败')
          } else {
            reject('请求失败，请稍后重试')
          }
        }
      })
    })
  }
}

/**
 * 常见关键词映射表
 */
api.KEYWORDS = {
  // 飞行类
  FLYING: 'Flying',
  REACH: 'Reach',

  // 战斗类
  FIRST_STRIKE: 'First Strike',
  DOUBLE_STRIKE: 'Double Strike',
  TRAMPLE: 'Trample',
  MENACE: 'Menace',
  DEATHTOUCH: 'Deathtouch',

  // 防御类
  DEFENDER: 'Defender',
  INDESTRUCTIBLE: 'Indestructible',
  WARD: 'Ward',

  // 进攻类
  HASTE: 'Haste',
  VIGILANCE: 'Vigilance',
  RUSH: 'Rush',

  // 操控类
  FLASH: 'Flash',
  TAP: 'Tap',
  UNTAP: 'Untap',

  // 其他
  HEXPROOF: 'Hexproof',
  SHROUD: 'Shroud',
  PROTECTION: 'Protection',
  EVOKE: 'Evoke',
  EXPLOIT: 'Exploit'
}

/**
 * 中文关键词到英文的映射
 */
api.CN_KEYWORDS = {
  '飞行': 'Flying',
  '触死': 'Deathtouch',
  '先攻': 'First Strike',
  '警戒': 'Vigilance',
  '闪现': 'Flash',
  '死触': 'Deathtouch',
  '威慑': 'Menace',
  '祭献': 'Evoke',
  '践踏': 'Trample',
  '双重打击': 'Double Strike',
  '辟邪': 'Hexproof',
  '不可阻挡': 'Indestructible',
  '守护': 'Ward',
  '极速': 'Haste',
  '到达': 'Reach'
}

/**
 * 中文转英文关键词
 * @param {string} cnKeyword - 中文关键词
 * @returns {string} 英文关键词
 */
api.getCnKeyword = function(cnKeyword) {
  return this.CN_KEYWORDS[cnKeyword] || cnKeyword
}

/**
 * 搜索规则（支持中文关键词）
 * @param {string} keyword - 搜索关键词（支持中文）
 * @returns {Promise}
 */
api.searchRulesCn = function(keyword) {
  return this.searchRules(keyword)
}

/**
 * 查询关键词（支持中文）
 * @param {string} keyword - 关键词（支持中文）
 * @returns {Promise}
 */
api.getKeywordCn = function(keyword) {
  const enKeyword = this.getCnKeyword(keyword)
  return this.getKeyword(enKeyword)
}

module.exports = api
