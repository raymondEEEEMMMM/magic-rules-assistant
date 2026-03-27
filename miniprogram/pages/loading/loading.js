Page({
  data: {
    currentText: '',
    progress: 0
  },

  loadingSteps: [
    { text: 'Agent知识库加载中...', progress: 20 },
    { text: '知识库已加载', progress: 40 },
    { text: '联网能力加载中...', progress: 60 },
    { text: '联网能力已加载', progress: 80 },
    { text: '准备就绪', progress: 100 }
  ],

  onLoad() {
    this.runLoadingSequence()
  },

  runLoadingSequence() {
    let stepIndex = 0

    const nextStep = () => {
      if (stepIndex < this.loadingSteps.length) {
        const step = this.loadingSteps[stepIndex]

        this.setData({
          currentText: step.text,
          progress: step.progress
        })

        stepIndex++

        // 最后一步完成后，跳转到首页
        if (stepIndex < this.loadingSteps.length) {
          setTimeout(nextStep, 1200)
        } else {
          setTimeout(() => {
            wx.redirectTo({
              url: '/pages/index/index'
            })
          }, 800)
        }
      }
    }

    // 开始第一步
    nextStep()
  }
})
