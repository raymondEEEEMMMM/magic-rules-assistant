"""
万智牌规则自动下载和更新服务
支持从官网下载最新规则（TXT格式，便于向量化）
"""
import os
import re
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuleDownloader:
    """规则下载器"""

    # 万智牌规则下载地址（TXT格式）
    RULES_BASE_URL = "https://media.wizards.com/2026/downloads/"
    RULES_FILENAME = "MagicCompRules 20260227.txt"
    RULES_INFO_FILENAME = "rules_info.json"

    # 数据目录
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data", "rules")

    def __init__(self):
        """初始化下载器"""
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def download_rules(self, force: bool = False) -> Dict:
        """
        下载最新规则

        Args:
            force: 是否强制下载（即使有本地缓存）

        Returns:
            下载结果字典
        """
        logger.info("开始检查规则更新...")

        # 获取在线版本信息
        online_info = self._get_online_rules_info()
        if not online_info:
            return {
                "success": False,
                "message": "无法获取在线规则信息"
            }

        # 检查本地版本
        local_info = self._get_local_rules_info()

        # 判断是否需要下载
        if not force and local_info:
            if self._is_latest_version(local_info, online_info):
                logger.info("本地规则已是最新版本")
                return {
                    "success": True,
                    "message": "本地规则已是最新版本",
                    "version": local_info.get("version"),
                    "date": local_info.get("date")
                }

        # 下载规则文件
        logger.info(f"开始下载规则: {online_info['version']} ({online_info['date']})")
        download_result = self._download_rules_file(online_info)

        if download_result["success"]:
            # 保存版本信息
            self._save_rules_info(online_info)
            logger.info("规则下载完成")
            return {
                "success": True,
                "message": "规则下载完成",
                "version": online_info.get("version"),
                "date": online_info.get("date"),
                "file_path": download_result["file_path"],
                "size": download_result["size"]
            }
        else:
            return download_result

    def _get_online_rules_info(self) -> Optional[Dict]:
        """获取在线规则信息"""
        try:
            # 从文件名中提取版本和日期
            # 文件名格式: MagicCompRules 20260227.txt
            version_match = re.search(r'(\d{4})', self.RULES_FILENAME)
            date_match = re.search(r'(\d{8})', self.RULES_FILENAME)

            if not version_match or not date_match:
                return None

            version = version_match.group(1)
            date_str = date_match.group(1)
            # 转换日期格式: 20260227 -> 2026/02/27
            formatted_date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"

            return {
                "version": version,
                "date": formatted_date,
                "url": f"{self.RULES_BASE_URL}{self.RULES_FILENAME}",
                "updated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"获取在线规则信息失败: {e}")
            return None

    def _download_rules_file(self, rules_info: Dict) -> Dict:
        """下载规则文件"""
        try:
            url = rules_info["url"]
            logger.info(f"下载地址: {url}")

            # 下载文件
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            # 保存文件
            file_path = os.path.join(self.DATA_DIR, self.RULES_FILENAME)
            total_size = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)

            logger.info(f"文件已保存: {file_path}")
            logger.info(f"文件大小: {total_size / 1024:.2f} KB")

            # 验证文件
            if not self._validate_rules_file(file_path):
                return {
                    "success": False,
                    "message": "下载的文件验证失败"
                }

            return {
                "success": True,
                "file_path": file_path,
                "size": total_size
            }

        except Exception as e:
            logger.error(f"下载规则文件失败: {e}")
            return {
                "success": False,
                "message": f"下载失败: {str(e)}"
            }

    def _validate_rules_file(self, file_path: str) -> bool:
        """验证规则文件"""
        try:
            if not os.path.exists(file_path):
                return False

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 1000:  # 至少1KB
                logger.warning(f"文件大小异常: {file_size} bytes")
                return False

            # 检查文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # 读取前1000字符

                # 检查是否包含规则特征
                if 'Comprehensive Rules' not in content and 'comprehensive rules' not in content:
                    logger.warning("文件内容不符合规则文件特征")
                    return False

            logger.info("文件验证通过")
            return True

        except Exception as e:
            logger.error(f"验证文件失败: {e}")
            return False

    def _get_local_rules_info(self) -> Optional[Dict]:
        """获取本地规则信息"""
        info_path = os.path.join(self.DATA_DIR, self.RULES_INFO_FILENAME)

        if not os.path.exists(info_path):
            return None

        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取本地规则信息失败: {e}")
            return None

    def _save_rules_info(self, rules_info: Dict):
        """保存规则信息"""
        info_path = os.path.join(self.DATA_DIR, self.RULES_INFO_FILENAME)

        try:
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(rules_info, f, ensure_ascii=False, indent=2)
            logger.info(f"规则信息已保存: {info_path}")
        except Exception as e:
            logger.error(f"保存规则信息失败: {e}")

    def _is_latest_version(self, local_info: Dict, online_info: Dict) -> bool:
        """检查本地是否是最新版本"""
        try:
            local_version = local_info.get("version")
            online_version = online_info.get("version")

            local_date = local_info.get("date")
            online_date = online_info.get("date")

            # 比较版本和日期
            if local_version and online_version and local_date and online_date:
                is_latest = (local_version == online_version and
                            local_date == online_date)
                logger.info(f"本地版本: {local_version} ({local_date})")
                logger.info(f"在线版本: {online_version} ({online_date})")
                return is_latest

            return False

        except Exception as e:
            logger.error(f"比较版本失败: {e}")
            return False

    def parse_rules(self) -> Dict:
        """
        解析规则文件，提取结构化数据

        Returns:
            解析结果字典
        """
        file_path = os.path.join(self.DATA_DIR, self.RULES_FILENAME)

        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": "规则文件不存在，请先下载"
            }

        logger.info("开始解析规则文件...")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取规则条目
            rules = self._extract_rules(content)

            # 提取关键词异能
            keyword_abilities = self._extract_keyword_abilities(content)

            # 提取术语表
            glossary = self._extract_glossary(content)

            logger.info(f"解析完成: {len(rules)} 条规则, {len(keyword_abilities)} 个关键词, {len(glossary)} 个术语")

            return {
                "success": True,
                "rules": rules,
                "keyword_abilities": keyword_abilities,
                "glossary": glossary
            }

        except Exception as e:
            logger.error(f"解析规则文件失败: {e}")
            return {
                "success": False,
                "message": f"解析失败: {str(e)}"
            }

    def _extract_rules(self, content: str) -> List[Dict]:
        """
        提取规则条目

        规则格式示例:
        100.1. These Magic rules apply to any Magic game with two or more players...
        """
        rules = []

        # 匹配规则编号和内容
        # 格式: 数字.数字.内容
        rule_pattern = re.compile(
            r'^(\d{3}\.?\d*\.?\d*)\s+(.+?)(?=\n\d{3}\.|$)',
            re.MULTILINE | re.DOTALL
        )

        matches = rule_pattern.finditer(content)

        for match in matches:
            rule_number = match.group(1)
            rule_content = match.group(2).strip()

            # 清理内容（移除多余的空格和换行）
            rule_content = re.sub(r'\s+', ' ', rule_content)

            # 跳过过短的规则
            if len(rule_content) < 10:
                continue

            rules.append({
                "rule_number": rule_number,
                "content": rule_content
            })

        return rules

    def _extract_keyword_abilities(self, content: str) -> List[Dict]:
        """
        提取关键词异能

        格式示例:
        702.9. Flying
        """
        keyword_abilities = []

        # 查找702开头的规则（关键词异能）
        keyword_pattern = re.compile(
            r'^702\.\d+\.\s+(.+?)\n(.+?)(?=\n702\.|\n\d{3}\.|$)',
            re.MULTILINE | re.DOTALL
        )

        matches = keyword_pattern.finditer(content)

        for match in matches:
            keyword_name = match.group(1).strip()
            keyword_content = match.group(2).strip()

            # 提取描述（通常在第一个句号前）
            description = ""
            desc_match = re.match(r'^(.+?[。.])', keyword_content)
            if desc_match:
                description = desc_match.group(1)

            keyword_abilities.append({
                "keyword_name": keyword_name,
                "description": description,
                "full_text": keyword_content
            })

        return keyword_abilities

    def _extract_glossary(self, content: str) -> List[Dict]:
        """
        提取术语表

        格式示例:
        Ability
        "Ability" and "effect" are often confused with one another...
        """
        glossary = []

        # 查找术语表部分
        glossary_start = content.find("Glossary")
        if glossary_start == -1:
            return glossary

        glossary_content = content[glossary_start:]

        # 提取术语定义
        glossary_pattern = re.compile(
            r'^([A-Z][^\n]+?)\n"([^"]+)"',
            re.MULTILINE
        )

        matches = glossary_pattern.finditer(glossary_content)

        for match in matches:
            term = match.group(1).strip()
            definition = match.group(2).strip()

            glossary.append({
                "term": term,
                "definition": definition
            })

        return glossary

    def get_rules_for_vectorization(self) -> Dict:
        """
        获取适合向量化的规则数据

        Returns:
            包含规则文本和元数据的字典
        """
        parse_result = self.parse_rules()

        if not parse_result["success"]:
            return {
                "success": False,
                "message": "解析失败"
            }

        # 准备向量化数据
        texts = []
        metadata = []

        # 添加规则条目
        for rule in parse_result["rules"]:
            texts.append(rule["content"])
            metadata.append({
                "type": "rule",
                "number": rule["rule_number"]
            })

        # 添加关键词异能
        for ka in parse_result["keyword_abilities"]:
            texts.append(ka["full_text"])
            metadata.append({
                "type": "keyword",
                "name": ka["keyword_name"]
            })

        # 添加术语定义
        for term in parse_result["glossary"]:
            texts.append(term["definition"])
            metadata.append({
                "type": "glossary",
                "term": term["term"]
            })

        return {
            "success": True,
            "texts": texts,
            "metadata": metadata,
            "total_count": len(texts)
        }


if __name__ == "__main__":
    # 测试下载器
    downloader = RuleDownloader()

    # 下载规则
    print("=" * 50)
    print("开始下载规则...")
    print("=" * 50)
    result = downloader.download_rules()
    print(f"\n下载结果: {result}")

    # 解析规则
    print("\n" + "=" * 50)
    print("开始解析规则...")
    print("=" * 50)
    parse_result = downloader.parse_rules()
    if parse_result["success"]:
        print(f"✓ 规则条目: {len(parse_result['rules'])}")
        print(f"✓ 关键词异能: {len(parse_result['keyword_abilities'])}")
        print(f"✓ 术语表: {len(parse_result['glossary'])}")

        # 显示示例
        if parse_result['rules']:
            print(f"\n规则示例:")
            print(f"{parse_result['rules'][0]['rule_number']}: {parse_result['rules'][0]['content'][:100]}...")

        if parse_result['keyword_abilities']:
            print(f"\n关键词示例:")
            ka = parse_result['keyword_abilities'][0]
            print(f"{ka['keyword_name']}: {ka['description']}")

    # 获取向量化数据
    print("\n" + "=" * 50)
    print("准备向量化数据...")
    print("=" * 50)
    vector_data = downloader.get_rules_for_vectorization()
    if vector_data["success"]:
        print(f"✓ 总文本数: {vector_data['total_count']}")
        print(f"✓ 可用于向量化")
