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
    openid: null,  // 用户 openid
    isLoading: true,  // 初始加载状态
    loadingText: '知识库已加载...',
    loadingStep: 1,  // 加载步骤
    thinkingStep: 0,  // 思维链步骤
    thinkingText: '收到你的问题...'  // 思维链文字
  },

  onLoad() {
    this.setData({ isLightTheme: true })
    this.initOpenid()
    this.loadHistory()
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

  // 加载历史记录
  loadHistory() {
    const that = this
    const openid = this.data.openid
    if (!openid) {
      console.log('loadHistory: 没有 openid，跳过')
      this.setData({ isLoading: false })
      return
    }

    // 步骤1: 开始加载知识库
    this.setData({
      loadingStep: 1,
      loadingText: 'agent 知识库加载中...'
    })

    // 并行：获取会话列表 + 预热 Agent
    const historyPromise = api.aiJudgeHistory(openid)
    // 预热 Agent（不等待，只管发送）
    api.aiJudgeInit(openid).catch(err => {
      console.log('initAgent failed:', err)
    })

    // 先获取会话列表
    historyPromise.then(res => {
      // 步骤2: 知识库列表已加载
      that.setData({
        loadingStep: 2,
        loadingText: '知识库已加载...'
      })

      if (res && res.success && res.data) {
        const sessions = res.data.sessions || []
        if (sessions.length === 0) {
          // 没有历史会话，短暂显示"知识库已加载"后直接完成
          console.log('loadHistory: 没有历史会话')
          setTimeout(() => {
            that.setData({
              loadingStep: 4,
              loadingText: '已加载',
              isLoading: false
            })
          }, 300)
          return
        }

        // 有历史会话，加载最新一个会话的消息
        console.log('loadHistory: 发现', sessions.length, '个历史会话')
        const latestSession = sessions[0]
        that.setData({ sessionId: latestSession.sessionId })

        // 短暂延迟，让用户看到"知识库已加载"
        setTimeout(() => {
          // 步骤3: 开始加载联网能力（会话消息）
          that.setData({
            loadingStep: 3,
            loadingText: '联网能力加载中...'
          })

          // 加载该会话的消息
          api.aiJudgeHistory(openid, latestSession.sessionId).then(msgRes => {
            if (msgRes && msgRes.success && msgRes.data) {
              const messages = msgRes.data.messages || []
              if (messages.length > 0) {
                console.log('loadHistory: 加载了', messages.length, '条消息')
                const formattedMessages = messages.map(msg => {
                  const time = msg.timestamp ? that.formatTime(msg.timestamp) : ''
                  const cleanContent = that.cleanMessageContent(msg.content)
                  return {
                    role: msg.role,
                    content: cleanContent,
                    parsedNodes: parseMarkdown(cleanContent),
                    time: time
                  }
                })
                that.setData({ messages: formattedMessages })
              }
            }
            // 步骤4: 完成
            that.setData({
              loadingStep: 4,
              loadingText: '已加载',
              isLoading: false
            })
          }).catch(err => {
            console.error('loadHistory messages error:', err)
            that.setData({
              loadingStep: 4,
              loadingText: '已加载',
              isLoading: false
            })
          })
        }, 300)
      } else {
        setTimeout(() => {
          that.setData({
            loadingStep: 4,
            loadingText: '已加载',
            isLoading: false
          })
        }, 300)
      }
    }).catch(err => {
      console.error('loadHistory error:', err)
      that.setData({
        loadingStep: 4,
        loadingText: '已加载',
        isLoading: false
      })
    })
  },

  // 清洗消息内容（移除 OpenCLAW 加的 [Thu 2026-03-26 21:17 GMT+8] 前缀）
  cleanMessageContent(content) {
    if (!content) return ''
    // 匹配 [星期 YYYY-MM-DD HH:MM GMT+8] 格式的前缀
    return content.replace(/^\[([A-Za-z]{3}\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+)\]\s*/, '')
  },

  // 格式化时间戳
  formatTime(timestamp) {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
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

    // 开始思维链动画
    let thinkingTimer = null
    let elapsed = 0
    const thinkingSteps = [
      { time: 0, step: 1, text: '收到你的问题...' },
      { time: 1500, step: 2, text: '正在查询知识库...' },
      { time: 4000, step: 3, text: '正在联网搜索...' },
      { time: 7000, step: 4, text: '分析问题中...' },
      { time: 35000, step: 5, text: '异步处理中，请稍后刷新试', stop: true }
    ]

    const updateThinking = () => {
      const currentStep = thinkingSteps.find(s => elapsed < s.time) || thinkingSteps[thinkingSteps.length - 1]
      that.setData({
        thinkingStep: currentStep.step,
        thinkingText: currentStep.text
      })
      // 如果是最后一步，显示后停止动画
      if (currentStep.stop) {
        if (thinkingTimer) {
          clearInterval(thinkingTimer)
          thinkingTimer = null
        }
        that.setData({ thinkingStep: 0, thinkingText: '' })
      }
    }

    // 启动思维链计时器
    thinkingTimer = setInterval(() => {
      elapsed += 500
      updateThinking()
    }, 500)

    api.aiJudgeChat(message, this.data.sessionId, this.data.openid).then(res => {
      // 停止思维链计时器
      if (thinkingTimer) {
        clearInterval(thinkingTimer)
        thinkingTimer = null
      }

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
          scrollIntoView: `msg-${messages.length - 1}`,
          thinkingStep: 0,
          thinkingText: ''
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
          scrollIntoView: `msg-${messages.length - 1}`,
          thinkingStep: 0,
          thinkingText: ''
        })
      }
    }).catch(err => {
      console.error('API error:', err)
      if (thinkingTimer) {
        clearInterval(thinkingTimer)
      }
      that.setData({
        loading: false,
        thinkingStep: 0,
        thinkingText: ''
      })

      // 超时是异步处理中，提示用户刷新
      if (err === 'async_timeout') {
        wx.showToast({
          title: 'AI 正在思考中，请稍后刷新会话',
          icon: 'none',
          duration: 3000
        })
        return
      }

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
          api.aiJudgeClear(that.data.sessionId, that.data.openid).then(() => {
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

  // 再问一次（重新发送上一条用户消息）
  retryLast() {
    // 如果 AI 正在思考中，提示用户
    if (this.data.loading) {
      wx.showToast({
        title: 'AI 正在思考中，请稍候...',
        icon: 'none',
        duration: 2000
      })
      return
    }

    const messages = this.data.messages
    if (messages.length === 0) return

    // 找到最后一条用户消息
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        const userMessage = messages[i].content
        // 删除最后一条 AI 回复（如果存在）
        const newMessages = messages.slice(0, i + 1)

        this.setData({
          messages: newMessages,
          loading: true,
          scrollIntoView: `msg-${i}`
        })

        // 重新发送
        this.chat(userMessage)
        break
      }
    }
  },

  // 刷新消息（调用历史会话接口获取最新回复）
  refreshMessages() {
    const openid = this.data.openid
    const sessionId = this.data.sessionId
    if (!openid || !sessionId) return

    api.aiJudgeHistory(openid, sessionId).then(res => {
      if (res && res.success && res.data) {
        const messages = res.data.messages || []
        // 比较消息数量
        if (messages.length > this.data.messages.length) {
          // 有新消息，更新
          const formattedMessages = messages.map(msg => {
            const cleanContent = this.cleanMessageContent(msg.content)
            return {
              role: msg.role,
              content: cleanContent,
              parsedNodes: parseMarkdown(cleanContent),
              time: this.formatTime(msg.timestamp)
            }
          })
          this.setData({
            messages: formattedMessages,
            loading: false,
            scrollIntoView: `msg-${formattedMessages.length - 1}`
          })
          wx.showToast({ title: '已获取新回复', icon: 'success' })
        } else {
          wx.showToast({ title: '暂无新回复', icon: 'none' })
        }
      }
    }).catch(err => {
      console.error('refreshMessages error:', err)
      wx.showToast({ title: '刷新失败', icon: 'none' })
    })
  }
})
