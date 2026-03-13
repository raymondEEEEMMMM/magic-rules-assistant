// pages/rule/rule.js
const app = getApp()

Page({
  data: {
    query: '',
    rules: [],
    loading: false,
    searchDone: false
  },

  onLoad(options) {
    if (options.query) {
      this.setData({
        query: decodeURIComponent(options.query)
      })
      this.onSearch()
    }
  },

  onInput(e) {
    this.setData({ query: e.detail.value })
  },

  onSearch() {
    const query = this.data.query.trim()
    if (!query) return

    this.setData({ 
      loading: true,
      searchDone: false 
    })

    app.requestApi('/api/search', { q: query })
      .then(res => {
        this.setData({
          loading: false,
          searchDone: true,
          rules: res.results?.rules || []
        })
      })
      .catch(() => {
        this.setData({
          loading: false,
          searchDone: true
        })
      })
  }
})
