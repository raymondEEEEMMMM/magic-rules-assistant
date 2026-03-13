// pages/keyword/keyword.js
const app = getApp()

Page({
  data: {
    keyword: '',
    keywords: [],
    keywordDetail: null,
    searchDone: false
  },

  onLoad(options) {
    if (options.keyword) {
      this.setData({
        keyword: decodeURIComponent(options.keyword)
      })
      this.onSearch()
    } else {
      // 加载关键词列表
      this.loadKeywordList()
    }
  },

  onInput(e) {
    this.setData({ 
      keyword: e.detail.value,
      keywordDetail: null
    })
  },

  onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.setData({ 
      searchDone: false 
    })

    app.requestApi('/api/keyword', { k: keyword })
      .then(res => {
        this.setData({
          searchDone: true,
          keywordDetail: res.result || null
        })
      })
      .catch(() => {
        this.setData({
          searchDone: true
        })
      })
  },

  loadKeywordList() {
    // 预定义常用关键词列表
    const commonKeywords = [
      'Flying', 'Deathtouch', 'First Strike', 'Double Strike', 'Lifelink',
      'Hexproof', 'Indestructible', 'Menace', 'Reach', 'Trample',
      'Vigilance', 'Haste', 'Flash', 'Fear', 'Intimidate',
      'Landfall', 'Storm', 'Affinity', 'Buyback', 'Cascade',
      'Changeling', 'Champion', 'Convoke', 'Dredge', 'Echo',
      'Enters the Battlefield', 'Leaves the Battlefield', 'Evolve', 'Extort',
      'Fateful Hour', 'Fight', 'Graft', 'Haunt', 'Heroic',
      'Imprint', 'Inspired', 'Join Forces', 'Kinship', 'Landfall',
      'Miracle', 'Morph', 'Ninjutsu', 'Outlast', 'Overload',
      'Partner', 'Persist', 'Phasing', 'Prowl', 'Raid',
      'Rebound', 'Regenerate', 'Replicate', 'Riot', 'Scavenge',
      'Soulshift', 'Splice', 'Split Second', 'Storm', 'Suspend',
      'Threshold', 'Transform', 'Tribute', 'Undaunted', 'Undergrowth'
    ]

    this.setData({ keywords: [] })
  },

  viewKeyword(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.onSearch()
  },

  goBack() {
    this.setData({
      keywordDetail: null,
      keyword: ''
    })
    this.loadKeywordList()
  }
})
