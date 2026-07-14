/**
 * utils 单元测试
 * 运行: 在 minitest 页面点击"运行测试"
 */

const storage = require('../utils/storage.js')

// ============= storage =============
function test_storage_set_and_get() {
  storage.set('test:key', { foo: 'bar' })
  const got = storage.get('test:key')
  if (JSON.stringify(got) !== JSON.stringify({ foo: 'bar' })) {
    throw new Error('expected {foo:bar}, got ' + JSON.stringify(got))
  }
}

function test_storage_get_with_default() {
  const got = storage.get('test:nonexistent', 'default-value')
  if (got !== 'default-value') {
    throw new Error('expected default-value, got ' + got)
  }
}

function test_storage_remove() {
  storage.set('test:to-remove', 'value')
  storage.remove('test:to-remove')
  const got = storage.get('test:to-remove')
  if (got !== undefined) {
    throw new Error('expected undefined, got ' + got)
  }
}

function test_storage_namespacing() {
  storage.set('a:key', 1, 'ns1')
  storage.set('a:key', 2, 'ns2')
  if (storage.get('a:key', null, 'ns1') !== 1) throw new Error('ns1 wrong')
  if (storage.get('a:key', null, 'ns2') !== 2) throw new Error('ns2 wrong')
}

module.exports = {
  'storage.set+get': test_storage_set_and_get,
  'storage.get default': test_storage_get_with_default,
  'storage.remove': test_storage_remove,
  'storage.namespace': test_storage_namespacing
}
