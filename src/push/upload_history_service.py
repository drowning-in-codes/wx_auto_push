import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UploadHistoryService:
    """管理已上传article id的记录"""

    def __init__(self, file_path="uploaded_articles.json"):
        """
        初始化上传历史服务
        :param file_path: 存储上传历史的JSON文件路径
        """
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        """加载上传历史数据"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载上传历史失败: {e}")
                return {}
        return {}

    def _save_data(self):
        """保存上传历史数据"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info(f"上传历史已保存到 {self.file_path}")
        except Exception as e:
            logger.error(f"保存上传历史失败: {e}")

    def is_uploaded(self, article_id):
        """
        检查article id是否已上传
        :param article_id: 文章ID
        :return: 如果已上传返回True，否则返回False
        """
        return article_id in self.data

    def add_uploaded_article(self, article_id, draft_media_id=None):
        """
        添加已上传的article id
        :param article_id: 文章ID
        :param draft_media_id: 草稿的media_id（可选）
        """
        if article_id not in self.data:
            self.data[article_id] = {
                "upload_time": datetime.now().isoformat(),
                "draft_media_id": draft_media_id,
            }
            self._save_data()
            logger.info(f"已添加上传记录: {article_id}")
        else:
            logger.warning(f"Article ID {article_id} 已存在于上传历史中")

    def get_upload_time(self, article_id):
        """
        获取article id的上传时间
        :param article_id: 文章ID
        :return: 上传时间字符串，如果不存在返回None
        """
        if article_id in self.data:
            return self.data[article_id].get("upload_time")
        return None

    def get_draft_media_id(self, article_id):
        """
        获取article id对应的草稿media_id
        :param article_id: 文章ID
        :return: 草稿media_id，如果不存在返回None
        """
        if article_id in self.data:
            return self.data[article_id].get("draft_media_id")
        return None

    def remove_uploaded_article(self, article_id):
        """
        移除已上传的article id
        :param article_id: 文章ID
        :return: 如果移除成功返回True，否则返回False
        """
        if article_id in self.data:
            del self.data[article_id]
            self._save_data()
            logger.info(f"已移除上传记录: {article_id}")
            return True
        return False

    def get_all_uploaded_articles(self):
        """
        获取所有已上传的article id
        :return: 已上传的article id列表
        """
        return list(self.data.keys())

    def get_upload_count(self):
        """
        获取已上传的article id数量
        :return: 已上传数量
        """
        return len(self.data)

    def clear_all(self):
        """清空所有上传历史"""
        self.data = {}
        self._save_data()
        logger.info("已清空所有上传历史")
