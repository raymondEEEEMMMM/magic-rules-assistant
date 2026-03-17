// utils/markdown.js

/**
 * Markdown 转微信小程序 rich-text 节点
 * 支持：标题、粗体、斜体、代码块、列表、链接
 */

function parseMarkdown(text) {
  if (!text) return []

  const nodes = []
  const lines = text.split('\n')

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i]

    // 跳过空行
    if (!line.trim()) {
      continue
    }

    // 标题处理
    if (line.startsWith('### ')) {
      nodes.push({
        name: 'h4',
        children: [{ type: 'text', text: line.slice(4) }]
      })
      continue
    }
    if (line.startsWith('## ')) {
      nodes.push({
        name: 'h3',
        children: [{ type: 'text', text: line.slice(3) }]
      })
      continue
    }
    if (line.startsWith('# ')) {
      nodes.push({
        name: 'h2',
        children: [{ type: 'text', text: line.slice(2) }]
      })
      continue
    }

    // 无序列表
    if (line.match(/^[-*] /)) {
      nodes.push({
        name: 'p',
        children: [{ type: 'text', text: '  • ' + parseInline(line.slice(2)) }]
      })
      continue
    }

    // 有序列表
    if (line.match(/^\d+\. /)) {
      const match = line.match(/^(\d+)\. (.*)$/)
      if (match) {
        nodes.push({
          name: 'p',
          children: [{ type: 'text', text: '  ' + match[1] + '. ' + parseInline(match[2]) }]
        })
        continue
      }
    }

    // 代码块（行内）
    if (line.includes('`') && !line.startsWith('```')) {
      nodes.push({
        name: 'p',
        children: parseInlineNodes(line)
      })
      continue
    }

    // 普通段落
    nodes.push({
      name: 'p',
      children: parseInlineNodes(line)
    })
  }

  return nodes
}

/**
 * 处理行内格式：粗体、斜体、代码
 */
function parseInline(text) {
  // 先处理代码块
  text = text.replace(/`([^`]+)`/g, '「$1」')
  // 粗体
  text = text.replace(/\*\*([^*]+)\*\*/g, '$1')
  // 斜体
  text = text.replace(/\*([^*]+)\*/g, '$1')
  return text
}

function parseInlineNodes(text) {
  const nodes = []
  let remaining = text
  let key = 0

  while (remaining) {
    // 匹配代码块
    const codeMatch = remaining.match(/^`([^`]+)`/)
    if (codeMatch) {
      nodes.push({
        name: 'span',
        attrs: { style: 'background-color: #f5f5f5; padding: 2rpx 6rpx; border-radius: 4rpx; font-family: monospace;' },
        children: [{ type: 'text', text: codeMatch[1] }]
      })
      remaining = remaining.slice(codeMatch[0].length)
      continue
    }

    // 匹配粗体
    const boldMatch = remaining.match(/^\*\*([^*]+)\*\*/)
    if (boldMatch) {
      nodes.push({
        name: 'strong',
        children: [{ type: 'text', text: boldMatch[1] }]
      })
      remaining = remaining.slice(boldMatch[0].length)
      continue
    }

    // 匹配斜体
    const italicMatch = remaining.match(/^\*([^*]+)\*/)
    if (italicMatch) {
      nodes.push({
        name: 'em',
        children: [{ type: 'text', text: italicMatch[1] }]
      })
      remaining = remaining.slice(italicMatch[0].length)
      continue
    }

    // 普通文本
    const plainText = remaining.match(/^[^*`]+/)
    if (plainText) {
      nodes.push({ type: 'text', text: plainText[0] })
      remaining = remaining.slice(plainText[0].length)
    } else {
      // 处理单个字符
      nodes.push({ type: 'text', text: remaining[0] })
      remaining = remaining.slice(1)
    }
  }

  return nodes
}

/**
 * 将 Markdown 文本转为简单纯文本（用于打字机效果）
 * 移除大部分格式标记，保留基本可读性
 */
function markdownToPlainText(text) {
  if (!text) return ''

  return text
    // 代码块
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    // 标题
    .replace(/^### /gm, '')
    .replace(/^## /gm, '')
    .replace(/^# /gm, '')
    // 粗体
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    // 斜体
    .replace(/\*([^*]+)\*/g, '$1')
    // 列表
    .replace(/^[-*] /gm, '• ')
    .replace(/^\d+\. /gm, '')
    // 链接
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // 清理多余空白
    .trim()
}

module.exports = {
  parseMarkdown,
  markdownToPlainText
}
