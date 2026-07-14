const iconUtil = require('../../utils/icon.js')

Page({
  data: {
    icons: iconUtil.listNames(),
    iconDataUrls: {}
  },
  onLoad() {
    const urls = {}
    this.data.icons.forEach(name => {
      urls[name] = iconUtil.getDataUrl(name, { size: 32 })
    })
    this.setData({ iconDataUrls: urls })
  }
})
