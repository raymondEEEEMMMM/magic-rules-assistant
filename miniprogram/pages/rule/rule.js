// pages/rule/rule.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    ruleNumber: '',
    loading: false,
    ruleDetail: null,
    error: null,
    showCn: true,
    isLightTheme: true
  },

  onLoad(options) {
    this.setData({ isLightTheme: true })
    if (options.rule) {
      this.setData({
        ruleNumber: decodeURIComponent(options.rule)
      })
      this.fetchRuleDetail()
    }
  },

  onShow() {
    this.setData({ isLightTheme: true })
  },

  // 返回
  goBack() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
  },

  // 获取规则详情
  fetchRuleDetail() {
    const ruleNumber = this.data.ruleNumber
    if (!ruleNumber) return

    this.setData({ loading: true, error: null })

    wx.showLoading({ title: '加载中...' })

    api.getRule(ruleNumber).then(res => {
      wx.hideLoading()

      if (res && res.result) {
        const detail = res.result
        // 按规则编号分段（如 702.9a, 702.9b）
        detail.contentLines_cn = this.splitByRuleNumber(detail.rule_content_cn || '')
        detail.contentLines_en = this.splitByRuleNumber(detail.rule_content_en || '')
        this.setData({
          loading: false,
          ruleDetail: detail
        })
      } else {
        this.setData({
          loading: false,
          error: '未找到规则'
        })
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('获取规则详情失败:', err)
      this.setData({
        loading: false,
        error: '加载失败'
      })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  // 切换语言
  switchLang(e) {
    const lang = e.currentTarget.dataset.lang
    this.setData({ showCn: lang === 'cn' })
  },

  // 去除 HTML 标签
  stripHtml(html) {
    return html.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').trim()
  },

  // 按规则编号分段（保持编号完整）
  splitByRuleNumber(content) {
    // 先去除 HTML 标签
    content = this.stripHtml(content)
    // 按规则编号分段（匹配如 702.9a, 702.9b, 101.1c 等）
    // 使用正则匹配：编号 + 内容，直到下一个编号或结束
    const parts = content.split(/(?=\d{3}\.\d+[a-z]?\s)/)
    return parts.filter(line => line.trim())
  }
})