// miniprogram/pages/mistake/add/add.js
const storage = require('../../../utils/mistakeStorage.js')

Page({
  data: {
    selectedType: '', // operation | rule | miss_trigger
    cards: [],        // 用户输入的牌名数组
    cardInput: '',    // 单个牌名输入
    title: '',
    content: ''
  },

  onTypeSelect(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ selectedType: type })
  },

  onCardInput(e) {
    this.setData({ cardInput: e.detail.value })
  },

  onAddCard() {
    const card = this.data.cardInput.trim()
    if (!card) return
    if (this.data.cards.includes(card)) return
    this.setData({
      cards: [...this.data.cards, card],
      cardInput: ''
    })
  },

  onRemoveCard(e) {
    const index = e.currentTarget.dataset.index
    const cards = [...this.data.cards]
    cards.splice(index, 1)
    this.setData({ cards })
  },

  onTitleInput(e) {
    this.setData({ title: e.detail.value })
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },

  onSave() {
    const { selectedType, title, content } = this.data
    if (!selectedType) {
      wx.showToast({ title: '请选择类型', icon: 'none' })
      return
    }
    if (!title.trim() && !content.trim()) {
      wx.showToast({ title: '请输入内容', icon: 'none' })
      return
    }

    storage.saveRecord({
      type: selectedType,
      cards: this.data.cards,
      title: title.trim(),
      content: content.trim()
    })

    wx.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => {
      wx.navigateBack()
    }, 1500)
  }
})
