"""
AI 裁判服务 - 基于 MiniMax API
"""
import json
import os
import requests
from typing import Dict, Optional, List
from config import Config


class AIJudgeService:
    """AI 裁判服务"""

    def __init__(self):
        self.api_key = Config.MINIMAX_API_KEY
        self.model = Config.MINIMAX_MODEL
        self.base_url = Config.MINIMAX_BASE_URL
        self.conversation_history: Dict[str, List[Dict]] = {}  # 按用户会话维护历史

        # 系统提示词
        self.system_prompt = """你是一位专业的万智牌裁判助手，精通万智牌 Comprehensive Rules（综合规则）。

## 你的职责
1. 回答玩家关于万智牌规则的问题
2. 分析对局情况，判断触发时机、费用支付、优先权等
3. 解释关键词异能和卡牌互动规则

## 回答规范
- 使用中文回答
- 引用具体的规则编号（如 CR 117.1、CR 504.1）
- 解释清晰，简明扼要
- 如果问题涉及多个规则，逐一说明

## 重要规则参考
- 堆叠（Stack）：咒语和异能在堆叠上 resolving
- 优先权（Priority）：谁可以做什么
- 触发式异能（Triggered Abilities）：何时触发、如何进入堆叠
- 伤害步骤（Combat Damage）：伤害如何分配

如果不确定某些细节，请明确说明并给出合理的推测。"""

    def _call_api(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """调用 MiniMax API"""
        if not self.api_key:
            return None

        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            print(f"MiniMax API 调用失败: {e}")
            return None

    def chat(self, user_message: str, session_id: str = "default") -> Dict:
        """
        与 AI 裁判对话

        Args:
            user_message: 用户消息
            session_id: 会话ID，用于维护对话历史

        Returns:
            {"success": bool, "reply": str}
        """
        if not self.api_key:
            return {
                "success": False,
                "reply": "AI 裁判服务暂未配置，请联系管理员。"
            }

        # 获取或初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]

        history = self.conversation_history[session_id]

        # 添加用户消息
        history.append({"role": "user", "content": user_message})

        # 调用 API
        reply = self._call_api(history)

        if reply:
            # 添加助手回复到历史
            history.append({"role": "assistant", "content": reply})

            # 限制历史长度（保留 system + 最近10轮对话）
            if len(history) > 21:
                self.conversation_history[session_id] = [history[0]] + history[-20:]

            return {
                "success": True,
                "reply": reply
            }
        else:
            return {
                "success": False,
                "reply": "AI 裁判暂时无法回答，请稍后再试。"
            }

    def analyze(self, request_data: Dict) -> Dict:
        """
        分析对局状态

        Args:
            request_data: 包含 game_state, cards, actions 等

        Returns:
            {"success": bool, "analysis": str}
        """
        if not self.api_key:
            return {
                "success": False,
                "analysis": "AI 裁判服务暂未配置。"
            }

        game_state = request_data.get("game_state", "")
        cards = request_data.get("cards", [])
        question = request_data.get("question", "")

        # 构建分析请求
        analysis_prompt = f"""请分析以下对局情况：

**对局描述：**
{game_state}

**相关卡牌：**
{chr(10).join([f"- {card}" for card in cards]) if cards else "无"}

**问题：**
{question}

请根据万智牌规则进行分析。"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]

        result = self._call_api(messages, temperature=0.5)

        if result:
            return {
                "success": True,
                "analysis": result
            }
        else:
            return {
                "success": False,
                "analysis": "分析失败，请稍后再试。"
            }

    def clear_session(self, session_id: str = "default"):
        """清除会话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# 全局实例
ai_judge_service = AIJudgeService()
