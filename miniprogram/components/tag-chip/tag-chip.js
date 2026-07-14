Component({
  properties: {
    text: { type: String, value: '' },
    active: { type: Boolean, value: false },
    color: { type: String, value: '' }
  },
  methods: { onTap() { this.triggerEvent('tap', { text: this.properties.text }) } }
})