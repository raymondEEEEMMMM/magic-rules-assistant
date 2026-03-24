// pages/agent/agent.js
const app = getApp()

// 引入 API 工具和 Markdown 工具
const api = require('../../utils/api')
const { markdownToPlainText, parseMarkdown } = require('../../utils/markdown')

// AI 头像（天平图标）
const AI_AVATAR = '⚖️'

Page({
  data: {
    inputValue: '',
    messages: [],
    loading: false,
    scrollIntoView: '',
    aiAvatar: AI_AVATAR,
    shortMode: false,  // 简洁模式，减少 token 消耗
    sessionId: 'miniprogram',  // 会话 ID
    isLightTheme: true,  // 默认日间主题
    openid: null  // 用户 openid
  },

  onLoad() {
    this.setData({ isLightTheme: true })
    this.initOpenid()
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 返回
  goBack() {
    wx.navigateBack()
  },

  // 初始化 openid
  initOpenid() {
    const that = this
    // 尝试从存储获取 openid
    const storedOpenid = wx.getStorageSync('userOpenid')
    if (storedOpenid) {
      this.setData({ openid: storedOpenid })
      return
    }

    // 如果没有存储的 openid，使用设备标识作为临时 openid
    // 注意：这不是真正的微信 openid，仅用于 per-user agent 隔离
    const deviceId = wx.getStorageSync('deviceId')
    if (deviceId) {
      this.setData({ openid: deviceId })
      return
    }

    // 生成临时设备 ID
    const tempId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    wx.setStorageSync('deviceId', tempId)
    this.setData({ openid: tempId })
  },

  // 使用示例问题
  useExample(e) {
    const question = e.currentTarget.dataset.q
    this.setData({ inputValue: question })
    this.sendMessage()
  },

  // 切换日间/夜间主题
  toggleTheme() {
    const newTheme = app.toggleTheme()
    this.setData({ isLightTheme: newTheme })
  },

  // 切换模式
  setShortMode(e) {
    const mode = e.currentTarget.dataset.mode === 'true'
    this.setData({ shortMode: mode })
  },

  // 输入监听
  onInput(e) {
    this.setData({
      inputValue: e.detail.value
    })
  },

  // 发送消息
  sendMessage() {
    const content = this.data.inputValue.trim()
    if (!content || this.data.loading) return

    // 添加用户消息
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

    const newMessages = [...this.data.messages, {
      role: 'user',
      content: content,
      time: timeStr
    }]

    this.setData({
      messages: newMessages,
      inputValue: '',
      loading: true,
      scrollIntoView: `msg-${newMessages.length - 1}`
    })

    // 调用 AI 裁判 API
    this.chat(content)
  },

  // 聊天
  chat(message) {
    const that = this

    api.aiJudgeChat(message, this.data.sessionId, this.data.openid).then(res => {
      // 更新时间戳
      const now = new Date()
      const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

      if (res && res.success && res.reply) {
        // 解析 Markdown 为 rich-text 节点
        const parsedNodes = parseMarkdown(res.reply)

        // 添加 AI 消息
        const messages = [...that.data.messages, {
          role: 'assistant',
          content: res.reply,
          parsedNodes: parsedNodes,
          time: timeStr
        }]

        that.setData({
          messages: messages,
          loading: false,
          scrollIntoView: `msg-${messages.length - 1}`
        })
      } else {
        // 添加错误消息
        const errorContent = res?.reply || '抱歉，我暂时无法回答。'
        const errorNodes = parseMarkdown(errorContent)

        const messages = [...that.data.messages, {
          role: 'assistant',
          content: errorContent,
          parsedNodes: errorNodes,
          time: timeStr
        }]

        that.setData({
          messages: messages,
          loading: false,
          scrollIntoView: `msg-${messages.length - 1}`
        })
      }
    }).catch(err => {
      console.error('API error:', err)
      const errorMsg = '网络错误，请检查网络后重试。'
      const now = new Date()
      const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

      const messages = [...that.data.messages, {
        role: 'assistant',
        content: errorMsg,
        parsedNodes: parseMarkdown(errorMsg),
        time: timeStr
      }]

      that.setData({
        messages: messages,
        loading: false,
        scrollIntoView: `msg-${messages.length - 1}`
      })
    })
  },

  // 新建会话
  newSession() {
    const that = this

    wx.showModal({
      title: '新建会话',
      content: '确定要开始新的对话吗？当前会话历史将被清除。',
      success(res) {
        if (res.confirm) {
          // 清除云端会话
          api.aiJudgeClear(that.data.sessionId).then(() => {
            // 清除本地会话历史
            that.setData({
              messages: [],
              sessionId: 'miniprogram_' + Date.now()  // 新的会话 ID
            })

            wx.showToast({
              title: '已新建会话',
              icon: 'success'
            })
          }).catch(err => {
            console.error('新建会话失败:', err)
            wx.showToast({
              title: '新建会话失败',
              icon: 'none'
            })
          })
        }
      }
    })
  },

  // 清除当前会话
  clearSession() {
    const that = this

    wx.showModal({
      title: '清除会话',
      content: '确定要清除当前对话记录吗？',
      success(res) {
        if (res.confirm) {
          that.setData({
            messages: []
          })

          wx.showToast({
            title: '已清除对话',
            icon: 'success'
          })
        }
      }
    })
  },

  // 清理 OpenCLAW 会话（清理服务器端过期会话历史）
  cleanupSessions() {
    const that = this

    wx.showModal({
      title: '清理会话',
      content: '确定要清理 OpenCLAW 过期会话吗？这可以解决响应超时问题。',
      success(res) {
        if (res.confirm) {
          wx.showLoading({ title: '清理中...' })

          api.cleanupSessions().then(result => {
            wx.hideLoading()
            console.log('清理会话结果:', result)
            wx.showToast({
              title: '已清理会话',
              icon: 'success'
            })
          }).catch(err => {
            wx.hideLoading()
            console.error('清理会话失败:', err)
            wx.showToast({
              title: '清理失败',
              icon: 'none'
            })
          })
        }
      }
    })
  }
})
