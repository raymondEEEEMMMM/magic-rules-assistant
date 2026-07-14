// components/token-card/token-card.js
Component({
  properties: {
    token: {
      type: Object,
      value: {}
    },
    isLightTheme: {
      type: Boolean,
      value: false
    }
  },

  methods: {
    onTap() {
      this.triggerEvent('tokenTap', { token: this.data.token })
    }
  }
})