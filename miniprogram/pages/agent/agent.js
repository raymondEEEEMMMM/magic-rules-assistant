// pages/agent/agent.js
const app = getApp()

// 引入 API 工具和 Markdown 工具
const api = require('../../utils/api')
const { markdownToPlainText, parseMarkdown } = require('../../utils/markdown')

// AI 头像（emoji 机器人图标）
const AI_AVATAR = '🤖'

Page({
  data: {
    inputValue: '',
    messages: [],
    loading: false,
    scrollIntoView: '',
    aiAvatar: AI_AVATAR,
    shortMode: false,  // 简洁模式，减少 token 消耗
    sessionId: 'miniprogram'  // 会话 ID
  },

  onLoad() {
    // 页面加载
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
    const newMessages = [...this.data.messages, {
      role: 'user',
      content: content
    }]

    // 添加空的 AI 消息占位
    const aiMessageIndex = newMessages.length
    newMessages.push({
      role: 'assistant',
      content: '',
      rawContent: '',
      parsedNodes: []
    })

    this.setData({
      messages: newMessages,
      inputValue: '',
      loading: true,
      scrollIntoView: `msg-${aiMessageIndex}`
    })

    // 调用 AI 裁判 API
    this.chat(content, aiMessageIndex)
  },

  // 聊天
  chat(message, aiMessageIndex) {
    const that = this
    const shortMode = this.data.shortMode
    const sessionId = this.data.sessionId

    api.aiJudgeChat(message, sessionId).then(res => {
      if (res && res.success && res.reply) {
        // 解析 Markdown 为 rich-text 节点
        const parsedNodes = parseMarkdown(res.reply)

        // 更新消息，保留原始内容和解析后的节点
        const messages = that.data.messages
        messages[aiMessageIndex] = {
          role: 'assistant',
          content: res.reply,  // 原始 Markdown 内容
          parsedNodes: parsedNodes   // 解析后的 rich-text 节点
        }

        that.setData({
          messages: messages,
          loading: false,
          scrollIntoView: `msg-${aiMessageIndex}`
        })
      } else {
        that.setData({
          messages: that.data.messages.map((msg, i) =>
            i === aiMessageIndex ? {
              ...msg,
              content: res?.reply || '抱歉，我暂时无法回答。',
              parsedNodes: parseMarkdown(res?.reply || '抱歉，我暂时无法回答。')
            } : msg
          ),
          loading: false
        })
      }
    }).catch(err => {
      console.error('API error:', err)
      const errorMsg = '网络错误，请检查网络后重试。'
      that.setData({
        messages: that.data.messages.map((msg, i) =>
          i === aiMessageIndex ? {
            ...msg,
            content: errorMsg,
            parsedNodes: parseMarkdown(errorMsg)
          } : msg
        ),
        loading: false
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
  }
})
