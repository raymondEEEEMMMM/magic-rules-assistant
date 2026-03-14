// 创建简单的 PNG 图标
const fs = require('fs');
const path = require('path');

// 简单的 PNG 文件头和调色板
const createSimplePNG = (color, active = false) => {
  const width = 64;
  const height = 64;

  // 简化的 PNG 格式 (仅用于测试)
  // 这是一个最小化的 PNG 文件结构
  const colorRGB = active ? [233, 69, 96] : [139, 139, 139]; // #e94560 or #8b8b8b

  // 这里我们创建一个非常简化的 PNG 文件
  // 实际使用中应该使用真正的图像处理库
  const signature = Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);

  // IHDR chunk
  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(width, 0);
  ihdrData.writeUInt32BE(height, 4);
  ihdrData[8] = 8;  // bit depth
  ihdrData[9] = 2;  // color type (RGB)
  ihdrData[10] = 0; // compression
  ihdrData[11] = 0; // filter
  ihdrData[12] = 0; // interlace

  const ihdr = Buffer.concat([
    Buffer.from('IHDR'),
    ihdrData,
    Buffer.from([0, 0, 0, 0]) // CRC placeholder
  ]);

  // IDAT chunk (simplified - just solid color)
  const pixelData = Buffer.alloc(width * height * 3);
  for (let i = 0; i < pixelData.length; i += 3) {
    pixelData[i] = colorRGB[0];     // R
    pixelData[i + 1] = colorRGB[1]; // G
    pixelData[i + 2] = colorRGB[2]; // B
  }

  const idatData = Buffer.concat([
    Buffer.from([0x78, 0x9C]), // ZLIB header
    pixelData,
    Buffer.from([0x01, 0x00, 0x00]) // ZLIB footer
  ]);

  const idat = Buffer.concat([
    Buffer.from('IDAT'),
    idatData,
    Buffer.from([0, 0, 0, 0]) // CRC placeholder
  ]);

  // IEND chunk
  const iend = Buffer.concat([
    Buffer.from('IEND'),
    Buffer.alloc(0),
    Buffer.from([0xAE, 0x42, 0x60, 0x82]) // CRC
  ]);

  return Buffer.concat([signature, ihdr, idat, iend]);
};

console.log('创建简单的 PNG 图标...');

const icons = [
  { name: 'home.png', active: false },
  { name: 'home-active.png', active: true },
  { name: 'search.png', active: false },
  { name: 'search-active.png', active: true },
  { name: 'card.png', active: false },
  { name: 'card-active.png', active: true }
];

icons.forEach(icon => {
  try {
    const pngData = createSimplePNG('#e94560', icon.active);
    fs.writeFileSync(icon.name, pngData);
    console.log(`✓ ${icon.name} 创建成功`);
  } catch (error) {
    console.error(`✗ ${icon.name} 创建失败:`, error.message);
  }
});

console.log('图标创建完成!');
