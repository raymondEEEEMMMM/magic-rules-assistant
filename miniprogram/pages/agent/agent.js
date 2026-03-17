// pages/agent/agent.js
const app = getApp()

// 引入 Markdown 工具
const { markdownToPlainText } = require('../../utils/markdown')

// API 配置
const API_BASE = 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com'

// AI 头像（emoji 机器人图标）
const AI_AVATAR = '🤖'

Page({
  data: {
    inputValue: '',
    messages: [],
    loading: false,
    scrollIntoView: '',
    aiAvatar: AI_AVATAR
  },

  onLoad() {
    // 页面加载
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
      content: ''
    })

    this.setData({
      messages: newMessages,
      inputValue: '',
      loading: true,
      scrollIntoView: `msg-${aiMessageIndex}`
    })

    // 调用 AI 裁判流式 API
    this.streamChat(content, aiMessageIndex)
  },

  // 流式聊天
  streamChat(message, aiMessageIndex) {
    const that = this

    // 使用 wx.request 下载流式数据
    const task = wx.request({
      url: `${API_BASE}/api/ai-judge/chat/stream`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      enableChunked: true,  // 启用分块传输
      data: {
        message: message,
        session_id: 'miniprogram'
      },
      success(res) {
        // 如果不是分块传输，回退到普通模式
        that.setData({
          loading: false
        })
      },
      fail(err) {
        console.error('流式请求失败，回退到普通模式:', err)
        that.fallbackChat(message, aiMessageIndex)
      }
    })

    // 在 task 级别维护内容
    let fullContent = ''

    // 监听接收到数据
    task.onChunkReceived((res) => {
      const arrayBuffer = res.data
      const uint8Array = new Uint8Array(arrayBuffer)
      const text = new TextDecoder('utf-8').decode(uint8Array)

      console.log('收到 chunk:', text)

      // 解析 SSE 格式的数据
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6)
          if (dataStr === '[DONE]') {
            // 流结束
            that.setData({ loading: false })
            return
          }

          try {
            const data = JSON.parse(dataStr)
            if (data.content) {
              fullContent += data.content

              // 更新消息内容
              const messages = that.data.messages
              if (messages[aiMessageIndex]) {
                messages[aiMessageIndex].content = fullContent
                that.setData({
                  messages: messages,
                  scrollIntoView: `msg-${aiMessageIndex}`
                })
              }
            }
            if (data.done || data.error) {
              console.log('流结束, fullContent:', fullContent)
              that.setData({ loading: false })
            }
          } catch (e) {
            console.log('解析错误:', e, 'dataStr:', dataStr)
          }
        }
      }
    })
  },

  // 回退到普通 API（非流式）
  fallbackChat(message, aiMessageIndex) {
    const that = this

    wx.request({
      url: `${API_BASE}/api/ai-judge/chat`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        message: message,
        session_id: 'miniprogram'
      },
      success(res) {
        if (res.data && res.data.success) {
          // 逐步显示内容（模拟打字效果），先转换 Markdown 为纯文本
          const plainText = markdownToPlainText(res.data.reply)
          that.typewriterEffect(plainText, aiMessageIndex)
        } else {
          that.setData({
            messages: that.data.messages.map((msg, i) =>
              i === aiMessageIndex ? { ...msg, content: res.data?.reply || '抱歉，我暂时无法回答。' } : msg
            ),
            loading: false
          })
        }
      },
      fail(err) {
        console.error('API error:', err)
        that.setData({
          messages: that.data.messages.map((msg, i) =>
            i === aiMessageIndex ? { ...msg, content: '网络错误，请检查网络后重试。' } : msg
          ),
          loading: false
        })
      }
    })
  },

  // 打字机效果
  typewriterEffect(fullText, aiMessageIndex) {
    const that = this
    let currentIndex = 0
    const speed = 30 // 每个字符间隔毫秒

    const messages = that.data.messages

    function typeNextChar() {
      if (currentIndex < fullText.length) {
        const currentContent = messages[aiMessageIndex].content || ''
        messages[aiMessageIndex].content = currentContent + fullText[currentIndex]

        that.setData({
          messages: messages,
          scrollIntoView: `msg-${aiMessageIndex}`
        })

        currentIndex++
        setTimeout(typeNextChar, speed)
      } else {
        that.setData({ loading: false })
      }
    }

    typeNextChar()
  }
})
