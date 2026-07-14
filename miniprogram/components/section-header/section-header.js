Component({
  properties: {
    title: { type: String, value: '' },
    count: { type: Number, value: null },
    moreText: { type: String, value: '' }
  },
  methods: { onMore() { this.triggerEvent('more') } }
})