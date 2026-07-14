const iconUtil = require('../../utils/icon.js')

Component({
  properties: {
    icon: { type: String, value: 'search' },
    title: { type: String, value: '' },
    desc: { type: String, value: '' },
    actionText: { type: String, value: '' }
  },
  data: { iconDataUrl: '' },
  lifetimes: {
    attached() {
      this.setData({ iconDataUrl: iconUtil.getDataUrl(this.properties.icon, { size: 56 }) })
    }
  },
  methods: { onAction() { this.triggerEvent('action') } }
})