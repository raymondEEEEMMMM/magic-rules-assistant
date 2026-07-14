const iconUtil = require('../../utils/icon.js')

Component({
  properties: {
    title: { type: String, value: '' },
    subtitle: { type: String, value: '' },
    showBack: { type: Boolean, value: false },
    showTheme: { type: Boolean, value: false }
  },
  data: { backIcon: '', themeIcon: '', isLightTheme: true },
  lifetimes: {
    attached() {
      const themeUtil = require('../../utils/theme.js')
      this.setData({
        backIcon: iconUtil.getDataUrl('arrow-left'),
        themeIcon: iconUtil.getDataUrl(themeUtil.isLight() ? 'moon' : 'sun'),
        isLightTheme: themeUtil.isLight()
      })
    }
  },
  methods: {
    onBack() { this.triggerEvent('back') },
    onToggleTheme() { this.triggerEvent('toggletheme') }
  }
})