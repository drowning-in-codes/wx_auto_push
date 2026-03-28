import json
import os
from typing import List, Dict, Optional
from .base_storage import StorageBase


class JsonStorage(StorageBase):
    """
    JSON存储服务
    将插画信息存储到JSON文件中
    """

    def __init__(self, file_path: str = "data/illustrations.json"):
        """
        初始化JSON存储服务
        
        参数:
            file_path: JSON文件路径
        """
        self.file_path = file_path
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
        # 确保文件存在
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_data(self) -> List[Dict]:
        """
        加载JSON文件数据
        
        返回:
            List[Dict]: 插画信息列表
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self, data: List[Dict]):
        """
        保存数据到JSON文件
        
        参数:
            data: 插画信息列表
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_illustration(self, illustration: Dict) -> bool:
        """
        保存单个插画信息
        """
        try:
            data = self._load_data()
            # 检查是否已存在
            article_id = illustration.get('article_id')
            if article_id:
                # 查找并更新
                for i, item in enumerate(data):
                    if item.get('article_id') == article_id:
                        data[i] = illustration
                        self._save_data(data)
                        return True
                # 不存在则添加
                data.append(illustration)
                self._save_data(data)
                return True
            return False
        except Exception as e:
            print(f"保存插画失败: {e}")
            return False

    def save_illustrations(self, illustrations: List[Dict]) -> bool:
        """
        批量保存插画信息
        """
        try:
            data = self._load_data()
            # 创建article_id到索引的映射
            id_map = {item.get('article_id'): i for i, item in enumerate(data) if item.get('article_id')}
            
            for illustration in illustrations:
                article_id = illustration.get('article_id')
                if article_id:
                    if article_id in id_map:
                        # 更新现有记录
                        data[id_map[article_id]] = illustration
                    else:
                        # 添加新记录
                        data.append(illustration)
            
            self._save_data(data)
            return True
        except Exception as e:
            print(f"批量保存插画失败: {e}")
            return False

    def get_illustration(self, article_id: str) -> Optional[Dict]:
        """
        根据文章ID获取插画信息
        """
        try:
            data = self._load_data()
            for item in data:
                if item.get('article_id') == article_id:
                    return item
            return None
        except Exception as e:
            print(f"获取插画失败: {e}")
            return None

    def get_illustrations(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取插画列表
        """
        try:
            data = self._load_data()
            return data[offset:offset + limit]
        except Exception as e:
            print(f"获取插画列表失败: {e}")
            return []

    def update_illustration(self, article_id: str, illustration: Dict) -> bool:
        """
        更新插画信息
        """
        return self.save_illustration(illustration)

    def delete_illustration(self, article_id: str) -> bool:
        """
        删除插画信息
        """
        try:
            data = self._load_data()
            new_data = [item for item in data if item.get('article_id') != article_id]
            if len(new_data) != len(data):
                self._save_data(new_data)
                return True
            return False
        except Exception as e:
            print(f"删除插画失败: {e}")
            return False

    def search_illustrations(self, keyword: str, limit: int = 100) -> List[Dict]:
        """
        搜索插画
        """
        try:
            data = self._load_data()
            results = []
            keyword_lower = keyword.lower()
            
            for item in data:
                # 搜索标题、内容、标签
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                tags = item.get('tags', [])
                tag_str = ' '.join([tag.lower() for tag in tags])
                
                if (keyword_lower in title or 
                    keyword_lower in content or 
                    keyword_lower in tag_str):
                    results.append(item)
                    if len(results) >= limit:
                        break
            
            return results
        except Exception as e:
            print(f"搜索插画失败: {e}")
            return []