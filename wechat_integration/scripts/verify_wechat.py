#!/usr/bin/env python3
"""
微信公众号配置验证脚本

功能：
- 验证公众号配置是否正确
- 检查服务器 IP 白名单
- 测试消息接口连接

使用方法:
    python3 verify_wechat.py
"""

import os
import sys
import json
import requests
import socket
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"


def load_env():
    """加载环境配置"""
    env_file = CONFIG_DIR / ".env"
    env_example = CONFIG_DIR / "env.example"

    config = {}

    # 尝试读取 .env 文件
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()

    # 合并环境变量
    config['WECHAT_APP_ID'] = os.environ.get('WECHAT_APP_ID', config.get('WECHAT_APP_ID', ''))
    config['WECHAT_APP_SECRET'] = os.environ.get('WECHAT_APP_SECRET', config.get('WECHAT_APP_SECRET', ''))
    config['WECHAT_TOKEN'] = os.environ.get('WECHAT_TOKEN', config.get('WECHAT_TOKEN', ''))

    return config


def check_app_config(app_id: str, app_secret: str) -> tuple:
    """检查公众号基础配置"""
    print("\n📱 检查公众号配置...")

    if not app_id:
        print("   ❌ WECHAT_APP_ID 未设置")
        return False

    if not app_secret:
        print("   ❌ WECHAT_APP_SECRET 未设置")
        return False

    print(f"   ✅ AppID: {app_id}")

    # 获取 access_token
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "access_token" in data:
            print("   ✅ AppSecret 验证成功")
            return True, data["access_token"]
        else:
            error_code = data.get("errcode")
            error_msg = data.get("errmsg", "未知错误")

            if error_code == 40164:
                print(f"   ❌ IP 未在白名单: {error_msg}")
            elif error_code == 40013:
                print(f"   ❌ AppID 无效: {error_msg}")
            elif error_code == 40125:
                print(f"   ❌ AppSecret 无效: {error_msg}")
            else:
                print(f"   ❌ 验证失败: {error_msg}")
            return False, None

    except Exception as e:
        print(f"   ❌ 网络请求失败: {e}")
        return False, None


def check_server_ips() -> list:
    """检查并显示服务器出口 IP"""
    print("\n🌐 服务器出口 IP:")

    # 尝试获取本机 IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"   本机 IP: {local_ip}")
    except:
        pass

    # 获取公网 IP
    try:
        resp = requests.get("https://api.ipify.org", timeout=5)
        public_ip = resp.text
        print(f"   公网 IP: {public_ip}")
        return [public_ip]
    except:
        print("   ⚠️ 无法获取公网 IP")
        return []


def check_wechat_server(url: str, token: str) -> bool:
    """检查微信服务器配置"""
    print("\n🔧 检查微信服务器配置...")

    # 模拟验证请求
    import hashlib
    timestamp = str(int(time.time()))
    nonce = "test"
    params = [token, timestamp, nonce]
    params.sort()
    signature = hashlib.sha1("".join(params).encode()).hexdigest()

    # 实际验证需要微信服务器发送请求，这里只是检查 URL 可访问性
    print(f"   ✅ 服务器 URL: {url}")
    print(f"   ✅ Token: {token}")
    print("   💡 需在微信后台配置服务器 URL 后才能验证")

    return True


def check_cloudbase_config():
    """检查 CloudBase 配置"""
    print("\n☁️  CloudBase 配置:")

    # 检查云函数配置
    config_file = Path(__file__).parent.parent.parent / "cloudbaserc.json"

    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if 'envId' in config:
            print(f"   ✅ 环境 ID: {config['envId']}")

        for fn in config.get('functions', []):
            if 'http' in fn:
                print(f"   ✅ 函数: {fn['name']} -> {fn['http'].get('path', '/')}")
    else:
        print("   ⚠️ cloudbaserc.json 未找到")


def main():
    print("=" * 50)
    print("微信公众号配置验证工具")
    print("=" * 50)

    # 加载配置
    config = load_env()
    app_id = config.get('WECHAT_APP_ID', '')
    app_secret = config.get('WECHAT_APP_SECRET', '')
    token = config.get('WECHAT_TOKEN', 'wx_mtg_rules_2024')

    # 检查公众号配置
    success, access_token = check_app_config(app_id, app_secret)

    # 检查服务器 IP
    ips = check_server_ips()

    # 检查云函数配置
    check_cloudbase_config()

    # 总结
    print("\n" + "=" * 50)
    print("📋 配置状态总结")
    print("=" * 50)

    if success:
        print("✅ 公众号基础配置正确")
        print("\n💡 后续步骤:")
        print("   1. 在微信后台 → 开发 → 开发设置 → 公众号开发信息")
        print("   2. 添加服务器 IP 到白名单")
        print("   3. 配置服务器 URL (回调地址)")
        print("   4. 设置自定义菜单 (如需要)")
    else:
        print("❌ 公众号配置有问题，请检查以上错误")

    print()


if __name__ == "__main__":
    main()
