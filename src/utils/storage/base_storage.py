from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class StorageBase(ABC):
    """
    存储服务基类
    定义存储服务的基本接口
    """

    @abstractmethod
    def save_illustration(self, illustration: Dict) -> bool:
        """
        保存单个插画信息
        
        参数:
            illustration: 插画信息字典
            
        返回:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def save_illustrations(self, illustrations: List[Dict]) -> bool:
        """
        批量保存插画信息
        
        参数:
            illustrations: 插画信息列表
            
        返回:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def get_illustration(self, article_id: str) -> Optional[Dict]:
        """
        根据文章ID获取插画信息
        
        参数:
            article_id: 文章ID
            
        返回:
            Optional[Dict]: 插画信息字典，如果不存在返回None
        """
        pass

    @abstractmethod
    def get_illustrations(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取插画列表
        
        参数:
            limit: 返回数量限制
            offset: 偏移量
            
        返回:
            List[Dict]: 插画信息列表
        """
        pass

    @abstractmethod
    def update_illustration(self, article_id: str, illustration: Dict) -> bool:
        """
        更新插画信息
        
        参数:
            article_id: 文章ID
            illustration: 插画信息字典
            
        返回:
            bool: 更新是否成功
        """
        pass

    @abstractmethod
    def delete_illustration(self, article_id: str) -> bool:
        """
        删除插画信息
        
        参数:
            article_id: 文章ID
            
        返回:
            bool: 删除是否成功
        """
        pass

    @abstractmethod
    def search_illustrations(self, keyword: str, limit: int = 100) -> List[Dict]:
        """
        搜索插画
        
        参数:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        返回:
            List[Dict]: 搜索结果列表
        """
        pass