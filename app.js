const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 80;

// 解析 JSON 和 URL 编码的请求体
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 启动 Python FastAPI 服务器
let pythonProcess;
function startPythonServer() {
  const pythonPath = path.join(__dirname, 'venv', 'bin', 'python');
  const scriptPath = path.join(__dirname, 'backend', 'main.py');

  pythonProcess = spawn(pythonPath, [scriptPath], {
    cwd: __dirname,
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    // 自动重启
    setTimeout(startPythonServer, 5000);
  });
}

// 代理所有请求到 Python FastAPI
app.all('*', async (req, res) => {
  const pythonPort = process.env.API_PORT || 8000;
  const targetUrl = `http://127.0.0.1:${pythonPort}${req.url}`;

  try {
    const http = require('http');
    const url = require('url');

    const urlObj = url.parse(targetUrl);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.path,
      method: req.method,
      headers: {
        ...req.headers,
        host: urlObj.host
      }
    };

    const proxyReq = http.request(options, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error('Proxy error:', err);
      res.status(500).json({ error: 'Python server not available' });
    });

    if (req.body) {
      proxyReq.write(JSON.stringify(req.body));
    }

    proxyReq.end();
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Node.js server running on port ${PORT}`);
  startPythonServer();
});

module.exports = app;
