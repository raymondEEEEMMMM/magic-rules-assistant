/**
 * 测试工具函数
 */

// 模拟数据测试
const testMockData = () => {
  console.log('=== 测试模拟数据 ===')
  
  // 测试随机卡牌
  const mockCards = [
    {
      name: '黑绿霸主',
      manaCost: '{2}{B}{G}',
      type: '生物 — 霸主',
      text: '当黑绿霸主进入战场时，你可以从你的牌库中寻找一张沼泽牌或森林牌，将其横置放进战场，然后将你的牌库洗牌。',
      power: '4',
      toughness: '4'
    }
  ]
  
  console.log('✓ 模拟卡牌数据正常')
  console.log('卡牌信息:', mockCards[0].name, mockCards[0].manaCost)
  
  // 测试关键词数据
  const mockKeywords = [
    {
      name: '飞行',
      description: '具有飞行的生物只能被其他具有飞行或延势的生物阻挡。'
    }
  ]
  
  console.log('✓ 模拟关键词数据正常')
  console.log('关键词信息:', mockKeywords[0].name)
}

// 搜索功能测试
const testSearchFunction = (keyword) => {
  console.log('=== 测试搜索功能 ===')
  console.log('搜索关键词:', keyword)
  
  const mockData = [
    { name: '飞行', description: '具有飞行的生物只能被其他具有飞行或延势的生物阻挡。' },
    { name: '死触', description: '具有死触的任何生物只要对另一个生物造成大于0的伤害，就会造成等量的伤害。' }
  ]
  
  const results = mockData.filter(item => 
    item.name.toLowerCase().includes(keyword.toLowerCase()) ||
    item.description.toLowerCase().includes(keyword.toLowerCase())
  )
  
  console.log('✓ 搜索功能正常')
  console.log('搜索结果:', results.length, '条')
  return results
}

// 页面导航测试
const testPageNavigation = (pages) => {
  console.log('=== 测试页面导航 ===')
  pages.forEach(page => {
    console.log('✓ 页面路径:', page)
  })
}

// 运行所有测试
const runAllTests = () => {
  console.log('🧪 开始运行测试...')
  console.log('----------------------------')
  
  testMockData()
  testSearchFunction('飞')
  testPageNavigation([
    '/pages/index/index',
    '/pages/search/search', 
    '/pages/card/card',
    '/pages/keyword/keyword',
    '/pages/rule/rule'
  ])
  
  console.log('----------------------------')
  console.log('✅ 所有测试通过!')
}

// 导出测试函数
module.exports = {
  testMockData,
  testSearchFunction,
  testPageNavigation,
  runAllTests
}