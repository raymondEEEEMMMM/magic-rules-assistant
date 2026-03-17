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

const API_BASE = 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com'

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
    return this.request('/wechat/api/search', { q: keyword })
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
    return this.request('/wechat/api/keyword', { k: keyword })
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
    return this.request('/wechat/api/mtgch/search', {
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
    return this.request('/wechat/api/mtgch/card', { id: cardId })
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
    return this.request('/wechat/api/mtgch/card', { set: setCode, number })
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
    return this.request('/wechat/api/mtgch/autocomplete', { q: query, size })
  },

  /**
   * 通用请求方法
   * @param {string} url - 请求路径
   * @param {object} data - 请求数据
   * @param {object} options - 额外配置
   * @returns {Promise}
   */
  request(url, data = {}, options = {}) {
    const { method = 'GET', showLoading = true } = options

    return new Promise((resolve, reject) => {
      if (showLoading) {
        wx.showLoading({ title: '加载中...' })
      }

      wx.request({
        url: API_BASE + url,
        data,
        method,
        header: {
          'content-type': 'application/json'
        },
        success(res) {
          if (showLoading) {
            wx.hideLoading()
          }

          if (res.statusCode !== 200) {
            reject(`请求失败: ${res.statusCode}`)
            return
          }

          if (res.data.error) {
            reject(res.data.error)
            return
          }

          resolve(res.data)
        },
        fail(err) {
          if (showLoading) {
            wx.hideLoading()
          }

          console.error('API 请求失败:', err)

          // 判断错误类型
          if (err.errMsg.includes('timeout')) {
            reject('请求超时，请检查网络')
          } else if (err.errMsg.includes('fail')) {
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
