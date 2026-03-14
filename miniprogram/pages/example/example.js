// API 使用示例页面

const api = require('../../utils/api.js')

Page({
  data: {
    keyword: '',
    results: [],
    keywordResult: null,
    cardResult: null,
    loading: false
  },

  // 输入框输入
  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  // 搜索规则
  handleSearchRules() {
    const { keyword } = this.data
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    api.searchRules(keyword)
      .then(data => {
        const rules = data.results.rules || []
        this.setData({ results: rules })

        if (rules.length === 0) {
          wx.showToast({ title: '未找到相关规则', icon: 'none' })
        }
      })
      .catch(err => {
        console.error(err)
        wx.showToast({ title: err, icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  // 查询关键词（支持中文）
  handleGetKeyword() {
    const { keyword } = this.data
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    api.getKeywordCn(keyword)
      .then(data => {
        const result = data.result
        this.setData({ keywordResult: result })

        if (result) {
          wx.showModal({
            title: result.keyword_name,
            content: result.full_text,
            showCancel: false
          })
        } else {
          wx.showToast({ title: '未找到该关键词', icon: 'none' })
        }
      })
      .catch(err => {
        console.error(err)
        wx.showToast({ title: err, icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  // 搜索卡牌
  handleSearchCard() {
    const { keyword } = this.data
    if (!keyword) {
      wx.showToast({ title: '请输入卡牌名称', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    api.searchCard(keyword)
      .then(data => {
        const cards = data.items || []
        this.setData({ cardResult: cards })

        if (cards.length > 0) {
          console.log('找到卡牌:', cards)
          wx.showToast({
            title: `找到 ${cards.length} 张卡牌`,
            icon: 'success'
          })
        } else {
          wx.showToast({ title: '未找到该卡牌', icon: 'none' })
        }
      })
      .catch(err => {
        console.error(err)
        wx.showToast({ title: err, icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  // 清空结果
  handleClear() {
    this.setData({
      results: [],
      keywordResult: null,
      cardResult: null
    })
  },

  // 测试服务状态
  handleTestStatus() {
    api.getStatus()
      .then(data => {
        wx.showModal({
          title: '服务状态',
          content: `状态: ${data.status}\n服务: ${data.service}`,
          showCancel: false
        })
      })
      .catch(err => {
        wx.showToast({ title: err, icon: 'none' })
      })
  }
})
