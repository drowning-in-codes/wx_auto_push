from typing import Optional
from .base_storage import StorageBase
from .json_storage import JsonStorage
from .database_storage import DatabaseStorage


class StorageFactory:
    """
    存储服务工厂
    用于创建和管理不同类型的存储服务
    """

    @staticmethod
    def create_storage(storage_type: str, **kwargs) -> Optional[StorageBase]:
        """
        创建存储服务
        
        参数:
            storage_type: 存储类型，可选值: 'json', 'database'
            **kwargs: 存储服务的参数
            
        返回:
            Optional[StorageBase]: 存储服务实例
        """
        if storage_type == 'json':
            file_path = kwargs.get('file_path', 'data/illustrations.json')
            return JsonStorage(file_path=file_path)
        elif storage_type == 'database':
            db_path = kwargs.get('db_path', 'data/illustrations.db')
            return DatabaseStorage(db_path=db_path)
        else:
            print(f"不支持的存储类型: {storage_type}")
            return None