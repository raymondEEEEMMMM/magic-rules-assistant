const iconUtil = require('../../utils/icon.js')

Component({
  properties: {
    icon: { type: String, value: '' },
    iconColor: { type: String, value: '' },
    title: { type: String, value: '' },
    desc: { type: String, value: '' },
    arrow: { type: Boolean, value: true },
    withDivider: { type: Boolean, value: false }
  },
  data: { chevronDataUrl: '', iconDataUrl: '' },
  lifetimes: {
    attached() {
      const data = { chevronDataUrl: iconUtil.getDataUrl('chevron-right') }
      if (this.properties.icon) {
        data.iconDataUrl = iconUtil.getDataUrl(this.properties.icon, { color: '#ffffff' })
      }
      this.setData(data)
    }
  },
  methods: { onTap() { this.triggerEvent('tap') } }
})