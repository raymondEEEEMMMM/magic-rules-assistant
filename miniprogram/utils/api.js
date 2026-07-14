/**
 * mtgAsk API 工具
 *
 * 使用 http.js 处理所有云函数调用。
 */

const http = require('./http.js')

const api = {
  searchRules(keyword) {
    if (!keyword || !keyword.trim()) return Promise.reject('请输入搜索关键词')
    return http.get('/api/search', { q: keyword })
  },
  getKeyword(keyword) {
    if (!keyword || !keyword.trim()) return Promise.reject('请输入关键词')
    return http.get('/api/keyword', { k: keyword })
  },
  getRule(ruleNumber) {
    if (!ruleNumber || !ruleNumber.trim()) return Promise.reject('请输入规则编号')
    return http.get('/api/rule', { n: ruleNumber })
  },
  searchCard(cardName, page, pageSize) {
    page = page || 1; pageSize = pageSize || 5
    if (!cardName || !cardName.trim()) return Promise.reject('请输入卡牌名称')
    return http.get('/api/card', { q: cardName, page: page, page_size: pageSize })
  },
  getStatus() { return http.get('/', {}) },
  getCardById(cardId) {
    if (!cardId) return Promise.reject('请输入卡牌ID')
    return http.get('/api/mtgch/card', { id: cardId })
  },
  getCardBySetAndNumber(setCode, number) {
    if (!setCode || !number) return Promise.reject('请输入系列代码和编号')
    return http.get('/api/mtgch/card', { set: setCode, number: number })
  },
  autocomplete(query, size) {
    size = size || 10
    if (!query || !query.trim()) return Promise.reject('请输入搜索内容')
    return http.get('/api/mtgch/autocomplete', { q: query, size: size })
  },
  getSetCards(setCode, page, pageSize) {
    page = page || 1; pageSize = pageSize || 20
    if (!setCode || !setCode.trim()) return Promise.reject('请输入系列代码')
    return http.get('/api/scryfall/set/' + setCode.toLowerCase() + '/cards/', { page: page })
  },
  getSecretLairCards(months) {
    months = months || 12
    return http.get('/api/secret-lair/cards', { months: months })
  },
  searchSecretLair(code) { return http.get('/api/secret-lair/search', { code: code }) },
  aiJudgeInit(openid) {
    if (!openid) return Promise.reject('openid 参数必填')
    return http.post('/api/ai-judge/init', { openid: openid })
  },
  aiJudgeChat(message, sessionId, openid) {
    sessionId = sessionId || 'miniprogram'
    if (!message || !message.trim()) return Promise.reject('请输入问题')
    const data = { message: message, session_id: sessionId }
    if (openid) data.openid = openid
    return http.post('/api/ai-judge/chat', data)
  },
  aiJudgeClear(sessionId, openid) {
    sessionId = sessionId || 'miniprogram'
    return http.post('/api/ai-judge/clear', { session_id: sessionId, openid: openid })
  },
  aiJudgeHistory(openid, sessionId, limit, offset) {
    limit = limit || 10; offset = offset || 0
    if (!openid) return Promise.reject('openid 参数必填')
    const data = { openid: openid, limit: limit, offset: offset }
    if (sessionId) data.session_id = sessionId
    return http.post('/api/ai-judge/history', data)
  },
  cleanupSessions() { return http.post('/api/admin/cleanup-sessions', {}) },
  submitFeedback(content, type, openid) {
    type = type || 'suggestion'; openid = openid || ''
    return http.post('/api/feedback', { content: content, type: type, openid: openid })
  },
  getAgentPoolStats() { return http.post('/api/admin/agent-pool/stats', {}) }
}

api.KEYWORDS = {
  FLYING: 'Flying', REACH: 'Reach', FIRST_STRIKE: 'First Strike',
  DOUBLE_STRIKE: 'Double Strike', TRAMPLE: 'Trample', MENACE: 'Menace',
  DEATHTOUCH: 'Deathtouch', DEFENDER: 'Defender', INDESTRUCTIBLE: 'Indestructible',
  WARD: 'Ward', HASTE: 'Haste', VIGILANCE: 'Vigilance', RUSH: 'Rush',
  FLASH: 'Flash', TAP: 'Tap', UNTAP: 'Untap', HEXPROOF: 'Hexproof',
  SHROUD: 'Shroud', PROTECTION: 'Protection', EVOKE: 'Evoke', EXPLOIT: 'Exploit'
}

api.CN_KEYWORDS = {
  '飞行': 'Flying', '死触': 'Deathtouch', '先攻': 'First Strike',
  '警戒': 'Vigilance', '闪现': 'Flash', '威慑': 'Menace',
  '呼魂': 'Evoke', '践踏': 'Trample', '连击': 'Double Strike',
  '辟邪': 'Hexproof', '不灭': 'Indestructible', '守护': 'Ward',
  '敏捷': 'Haste', '延势': 'Reach'
}

api.getCnKeyword = function(cn) { return this.CN_KEYWORDS[cn] || cn }
api.searchRulesCn = function(keyword) { return this.searchRules(keyword) }
api.getKeywordCn = function(keyword) {
  return this.getKeyword(this.getCnKeyword(keyword))
}

module.exports = api
