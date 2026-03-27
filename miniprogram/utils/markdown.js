// utils/markdown.js

/**
 * Markdown 转微信小程序 rich-text 节点
 * 支持：标题、粗体、斜体、代码块、列表、链接
 */

function parseMarkdown(text) {
  if (!text) return []

  const nodes = []
  const lines = text.split('\n')

  let i = 0
  while (i < lines.length) {
    let line = lines[i]

    // 代码块处理
    if (line.startsWith('```')) {
      // 收集代码块内容
      let codeContent = ''
      i++
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeContent += (codeContent ? '\n' : '') + lines[i]
        i++
      }
      nodes.push({
        name: 'p',
        attrs: { style: 'background-color: #f5f5f5; padding: 16rpx; border-radius: 8rpx; margin: 8rpx 0; font-family: monospace; font-size: 26rpx; white-space: pre-wrap; word-break: break-all;' },
        children: [{ type: 'text', text: codeContent }]
      })
      i++
      continue
    }

    // 跳过空行
    if (!line.trim()) {
      i++
      continue
    }

    // 标题处理
    if (line.startsWith('#### ')) {
      nodes.push({
        name: 'p',
        attrs: { style: 'font-size: 28rpx; font-weight: bold; color: #555; margin-top: 16rpx;' },
        children: [{ type: 'text', text: line.slice(5) }]
      })
      i++
      continue
    }
    if (line.startsWith('### ')) {
      nodes.push({
        name: 'p',
        attrs: { style: 'font-size: 30rpx; font-weight: bold; color: #333; margin-top: 16rpx;' },
        children: [{ type: 'text', text: line.slice(4) }]
      })
      i++
      continue
    }
    if (line.startsWith('## ')) {
      nodes.push({
        name: 'p',
        attrs: { style: 'font-size: 32rpx; font-weight: bold; color: #11998e; margin-top: 20rpx;' },
        children: [{ type: 'text', text: line.slice(3) }]
      })
      i++
      continue
    }
    if (line.startsWith('# ')) {
      nodes.push({
        name: 'p',
        attrs: { style: 'font-size: 36rpx; font-weight: bold; color: #11998e; margin: 16rpx 0;' },
        children: [{ type: 'text', text: line.slice(2) }]
      })
      i++
      continue
    }

    // 分隔线
    if (line.match(/^---+$/)) {
      nodes.push({
        name: 'p',
        attrs: { style: 'border-bottom: 1rpx solid #eee; margin: 16rpx 0;' },
        children: []
      })
      i++
      continue
    }

    // 表格处理
    if (line.startsWith('|') && line.includes('|')) {
      // 跳过表头分隔行
      if (line.match(/^\|[-:\s|]+\|$/)) {
        i++
        continue
      }
      // 解析表格行
      const cells = line.split('|').filter(c => c.trim())
      if (cells.length > 0) {
        let tableRow = { name: 'p', attrs: { style: 'margin: 4rpx 0;' }, children: [] }
        cells.forEach((cell, idx) => {
          const cellText = cell.trim()
          tableRow.children.push({
            type: 'text',
            text: (idx > 0 ? ' | ' : '') + cellText
          })
        })
        nodes.push(tableRow)
      }
      i++
      continue
    }

    // 无序列表
    if (line.match(/^[-*] /)) {
      nodes.push({
        name: 'p',
        attrs: { style: 'margin: 8rpx 0; padding-left: 16rpx;' },
        children: [{ type: 'text', text: '• ' + parseInline(line.slice(2)) }]
      })
      i++
      continue
    }

    // 有序列表
    if (line.match(/^\d+\. /)) {
      const match = line.match(/^(\d+)\. (.*)$/)
      if (match) {
        nodes.push({
          name: 'p',
          attrs: { style: 'margin: 8rpx 0; padding-left: 16rpx;' },
          children: [{ type: 'text', text: match[1] + '. ' + parseInline(match[2]) }]
        })
        i++
        continue
      }
    }

    // 引用块
    if (line.startsWith('> ')) {
      nodes.push({
        name: 'p',
        attrs: { style: 'border-left: 6rpx solid #11998e; padding-left: 16rpx; color: #666; margin: 12rpx 0; font-style: italic;' },
        children: [{ type: 'text', text: line.slice(2) }]
      })
      i++
      continue
    }

    // 普通段落 - 处理行内格式
    nodes.push({
      name: 'p',
      attrs: { style: 'margin: 8rpx 0; line-height: 1.6;' },
      children: parseInlineNodes(line)
    })
    i++
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
    // 移除表格分隔行
    .replace(/^\|[-:\s|]+\|$/gm, '')
    // 表格行
    .replace(/\|/g, ' | ')
    // 行内代码
    .replace(/`([^`]+)`/g, '$1')
    // 标题
    .replace(/^#### /gm, '')
    .replace(/^### /gm, '')
    .replace(/^## /gm, '')
    .replace(/^# /gm, '')
    // 分隔线
    .replace(/^---+$/gm, '')
    // 引用
    .replace(/^> /gm, '')
    // 粗体
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    // 斜体
    .replace(/\*([^*]+)\*/g, '$1')
    // 列表
    .replace(/^[-*] /gm, '• ')
    .replace(/^\d+\. /gm, '')
    // 链接
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // 多个空行合并为一个
    .replace(/\n{3,}/g, '\n\n')
    // 清理多余空白
    .trim()
}

module.exports = {
  parseMarkdown,
  markdownToPlainText
}
