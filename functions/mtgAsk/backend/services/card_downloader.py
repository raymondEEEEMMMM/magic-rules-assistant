"""
MTGJSON 卡牌数据下载器

支持从 MTGJSON 下载卡牌数据（SQLite 格式）并集成到规则系统。
"""

import os
import gzip
import shutil
import requests
from typing import Dict, Optional
from datetime import datetime
from config import Config


class CardDownloader:
    """MTGJSON 卡牌数据下载器"""

    # MTGJSON API 基础 URL
    BASE_URL = "https://mtgjson.com/api/v5"

    # 需要下载的文件
    DOWNLOAD_FILES = {
        "AllPrintings.sqlite.gz": {
            "description": "完整卡牌数据库",
            "type": "database",
            "compressed": True
        },
        "Keywords.json": {
            "description": "关键词异能定义",
            "type": "keywords",
            "compressed": False
        },
        "SetList.json": {
            "description": "系列列表",
            "type": "metadata",
            "compressed": False
        }
    }

    def __init__(self):
        """初始化下载器"""
        self.data_dir = os.path.join(os.path.dirname(__file__), "../data/mtg")
        self.ensure_directory()

    def ensure_directory(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"✓ 创建数据目录: {self.data_dir}")

    def download_file(self, filename: str, force: bool = False) -> Dict:
        """
        下载单个文件

        Args:
            filename: 文件名
            force: 是否强制重新下载

        Returns:
            下载结果字典
        """
        file_info = self.DOWNLOAD_FILES.get(filename)
        if not file_info:
            return {
                "success": False,
                "message": f"未知文件: {filename}"
            }

        url = f"{self.BASE_URL}/{filename}"
        local_path = os.path.join(self.data_dir, filename)

        # 检查文件是否已存在
        if os.path.exists(local_path) and not force:
            return {
                "success": True,
                "message": f"文件已存在: {filename}",
                "path": local_path
            }

        print(f"⬇️  下载: {filename}")
        print(f"   URL: {url}")

        try:
            # 下载文件
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # 保存文件
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = os.path.getsize(local_path) / 1024  # KB

            print(f"✓ 下载完成: {filename} ({file_size:.2f} KB)")

            # 如果是压缩文件，自动解压
            if file_info.get("compressed"):
                extracted_path = self._extract_file(local_path)
                if extracted_path:
                    return {
                        "success": True,
                        "message": f"下载并解压成功: {filename}",
                        "path": extracted_path
                    }

            return {
                "success": True,
                "message": f"下载成功: {filename}",
                "path": local_path
            }

        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"下载失败: {str(e)}"
            }

    def _extract_file(self, compressed_path: str) -> Optional[str]:
        """
        解压文件

        Args:
            compressed_path: 压缩文件路径

        Returns:
            解压后的文件路径
        """
        # 移除 .gz 或 .bz2 后缀
        if compressed_path.endswith('.gz'):
            extracted_path = compressed_path[:-3]
        elif compressed_path.endswith('.bz2'):
            extracted_path = compressed_path[:-4]
        else:
            return None

        try:
            print(f"📦 解压: {compressed_path}")

            with gzip.open(compressed_path, 'rb') as f_in:
                with open(extracted_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            file_size = os.path.getsize(extracted_path) / 1024  # KB
            print(f"✓ 解压完成: {extracted_path} ({file_size:.2f} KB)")

            return extracted_path

        except Exception as e:
            print(f"✗ 解压失败: {str(e)}")
            return None

    def download_all(self, force: bool = False) -> Dict:
        """
        下载所有需要的文件

        Args:
            force: 是否强制重新下载

        Returns:
            下载结果字典
        """
        print("=" * 60)
        print("🃏 MTGJSON 卡牌数据下载")
        print("=" * 60)

        results = []
        success_count = 0
        fail_count = 0

        for filename in self.DOWNLOAD_FILES.keys():
            result = self.download_file(filename, force=force)
            results.append(result)

            if result["success"]:
                success_count += 1
            else:
                fail_count += 1
                print(f"✗ {result['message']}")

        print("=" * 60)
        print(f"📊 下载完成: 成功 {success_count}, 失败 {fail_count}")
        print("=" * 60)

        return {
            "success": fail_count == 0,
            "total": len(results),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results
        }

    def get_database_path(self) -> Optional[str]:
        """
        获取 MTG 卡牌数据库路径

        Returns:
            数据库文件路径，如果不存在则返回 None
        """
        # 检查解压后的 SQLite 文件
        db_path = os.path.join(self.data_dir, "AllPrintings.sqlite")
        if os.path.exists(db_path):
            return db_path

        # 检查压缩文件
        gz_path = os.path.join(self.data_dir, "AllPrintings.sqlite.gz")
        if os.path.exists(gz_path):
            print(f"⚠️  检测到压缩文件，正在解压...")
            extracted_path = self._extract_file(gz_path)
            return extracted_path

        return None

    def get_keywords_path(self) -> Optional[str]:
        """
        获取关键词 JSON 文件路径

        Returns:
            关键词文件路径，如果不存在则返回 None
        """
        keywords_path = os.path.join(self.data_dir, "Keywords.json")
        if os.path.exists(keywords_path):
            return keywords_path
        return None

    def get_status(self) -> Dict:
        """
        获取下载状态

        Returns:
            状态信息字典
        """
        db_path = self.get_database_path()
        keywords_path = self.get_keywords_path()

        status = {
            "data_dir": self.data_dir,
            "database_exists": db_path is not None,
            "database_path": db_path,
            "database_size": None,
            "keywords_exists": keywords_path is not None,
            "keywords_path": keywords_path
        }

        if db_path and os.path.exists(db_path):
            status["database_size"] = os.path.getsize(db_path) / 1024 / 1024  # MB

        if keywords_path and os.path.exists(keywords_path):
            status["keywords_size"] = os.path.getsize(keywords_path) / 1024  # KB

        return status


if __name__ == "__main__":
    # 测试下载功能
    downloader = CardDownloader()

    # 查看状态
    status = downloader.get_status()
    print("\n📊 当前状态:")
    print(f"   数据目录: {status['data_dir']}")
    print(f"   数据库: {'✓' if status['database_exists'] else '✗'}")
    if status['database_size']:
        print(f"   数据库大小: {status['database_size']:.2f} MB")
    print(f"   关键词: {'✓' if status['keywords_exists'] else '✗'}")

    # 下载所有文件
    print("\n" + "=" * 60)
    result = downloader.download_all(force=False)

    if result["success"]:
        print("\n🎉 所有文件下载成功！")

        # 再次查看状态
        status = downloader.get_status()
        print(f"\n📊 数据库路径: {status['database_path']}")
        print(f"📊 关键词路径: {status['keywords_path']}")
    else:
        print(f"\n⚠️  部分文件下载失败: {result['fail_count']} 个失败")
