#!/usr/bin/env python3
"""
微信公众号菜单设置脚本

功能：
- 获取微信 access_token
- 创建自定义菜单
- 查询当前菜单配置

使用前提：
1. 已配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET
2. 已将服务器 IP 添加到白名单

使用方法:
    # 方式1：环境变量
    export WECHAT_APP_ID="your_app_id"
    export WECHAT_APP_SECRET="your_app_secret"
    python3 set_menu.py

    # 方式2：命令行参数
    python3 set_menu.py --app-id your_app_id --app-secret your_app_secret

菜单 Key 说明：
- keyword_search : 关键词查询说明
- rule_search    : 规则搜索说明
- card_search    : 卡牌查询说明
- feature_intro  : 功能介绍
- about          : 关于服务
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

# 当前目录
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"


def load_menu_config():
    """加载菜单配置"""
    menu_file = CONFIG_DIR / "menu.json"
    if menu_file.exists():
        with open(menu_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 默认配置
    return {
        "button": [
            {
                "name": "规则查询",
                "sub_button": [
                    {"type": "click", "name": "关键词查询", "key": "keyword_search"},
                    {"type": "click", "name": "规则搜索", "key": "rule_search"},
                    {"type": "click", "name": "卡牌查询", "key": "card_search"}
                ]
            },
            {
                "name": "使用帮助",
                "sub_button": [
                    {"type": "click", "name": "功能介绍", "key": "feature_intro"},
                    {"type": "click", "name": "关于服务", "key": "about"}
                ]
            }
        ]
    }


def get_access_token(app_id: str, app_secret: str) -> str:
    """获取微信 access_token"""
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
            return data["access_token"]
        else:
            error_msg = data.get("errmsg", "未知错误")
            print(f"❌ 获取 access_token 失败: {error_msg}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def create_menu(access_token: str, menu_config: dict) -> bool:
    """创建菜单"""
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create"
    params = {"access_token": access_token}

    try:
        resp = requests.post(url, params=params, json=menu_config, timeout=10)
        data = resp.json()

        if data.get("errcode") == 0:
            print("✅ 菜单创建成功!")
            return True
        else:
            error_msg = data.get("errmsg", "未知错误")
            print(f"❌ 菜单创建失败: {error_msg}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def get_menu(access_token: str) -> dict:
    """获取当前菜单"""
    url = "https://api.weixin.qq.com/cgi-bin/menu/get"
    params = {"access_token": access_token}

    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"❌ 获取菜单失败: {e}")
        return {}


def delete_menu(access_token: str) -> bool:
    """删除菜单"""
    url = "https://api.weixin.qq.com/cgi-bin/menu/delete"
    params = {"access_token": access_token}

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data.get("errcode") == 0
    except Exception as e:
        print(f"❌ 删除菜单失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="微信公众号菜单设置工具")
    parser.add_argument("--app-id", "-i", help="微信公众号 AppID")
    parser.add_argument("--app-secret", "-s", help="微信公众号 AppSecret")
    parser.add_argument("--action", "-a", choices=["create", "get", "delete"],
                        default="create", help="操作类型")
    args = parser.parse_args()

    # 获取配置
    app_id = args.app_id or os.environ.get("WECHAT_APP_ID", "")
    app_secret = args.app_secret or os.environ.get("WECHAT_APP_SECRET", "")

    print("=" * 50)
    print("微信公众号菜单设置工具")
    print("=" * 50)

    # 检查配置
    if not app_id or not app_secret:
        print("\n⚠️  请先配置微信公众号 AppID 和 AppSecret:")
        print("   方法1: 环境变量")
        print("     export WECHAT_APP_ID='your_app_id'")
        print("     export WECHAT_APP_SECRET='your_app_secret'")
        print("\n   方法2: 命令行参数")
        print("     python3 set_menu.py -i your_app_id -s your_app_secret")
        print(f"\n当前配置: APP_ID={'已设置' if app_id else '未设置'}")
        return

    print(f"\n📱 AppID: {app_id}")

    # 获取 access_token
    print("\n🔑 正在获取 access_token...")
    access_token = get_access_token(app_id, app_secret)

    if not access_token:
        print("\n❌ 无法获取 access_token，请检查:")
        print("   1. AppID 和 AppSecret 是否正确")
        print("   2. 服务器 IP 是否已添加到白名单")
        return

    print(f"✅ access_token 获取成功")

    # 执行操作
    if args.action == "create":
        print("\n📝 正在创建菜单...")
        menu_config = load_menu_config()
        if create_menu(access_token, menu_config):
            print("\n🎉 菜单设置完成! 请在微信中重新关注公众号以刷新菜单。")
        else:
            print("\n❌ 菜单创建失败")
            print("\n💡 可能的原因:")
            print("   - 订阅号未认证，没有自定义菜单 API 权限")
            print("   - 需手动在微信后台配置菜单")

    elif args.action == "get":
        print("\n📋 当前菜单配置:")
        menu = get_menu(access_token)
        print(json.dumps(menu, ensure_ascii=False, indent=2))

    elif args.action == "delete":
        print("\n🗑️ 正在删除菜单...")
        if delete_menu(access_token):
            print("✅ 菜单删除成功")
        else:
            print("❌ 菜单删除失败")


if __name__ == "__main__":
    main()
