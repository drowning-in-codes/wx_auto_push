import os
import tempfile
import json
import pytest
from src.push.upload_history_service import UploadHistoryService

class TestUploadHistoryService:
    """测试UploadHistoryService的功能"""

    def setup_method(self):
        """设置测试环境"""
        # 创建临时文件用于测试
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()
        
        # 确保文件不存在
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    def teardown_method(self):
        """清理测试环境"""
        # 清理临时文件
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
        # 清理临时文件的备份
        temp_backup = f"{self.temp_file_path}.tmp"
        if os.path.exists(temp_backup):
            os.remove(temp_backup)

    def test_first_write(self):
        """测试首次写入"""
        # 创建服务实例
        service = UploadHistoryService(self.temp_file_path)
        
        # 验证初始状态为空
        assert service.get_upload_count() == 0
        assert service.get_all_uploaded_articles() == []
        
        # 添加上传记录
        article_id = "12345"
        draft_media_id = "media_id_12345"
        service.add_uploaded_article(article_id, draft_media_id)
        
        # 验证记录已添加
        assert service.get_upload_count() == 1
        assert article_id in service.get_all_uploaded_articles()
        assert service.is_uploaded(article_id) is True
        assert service.get_draft_media_id(article_id) == draft_media_id
        assert service.get_upload_time(article_id) is not None

    def test_duplicate_write(self):
        """测试重复写入不覆盖"""
        # 创建服务实例
        service = UploadHistoryService(self.temp_file_path)
        
        # 添加上传记录
        article_id = "12345"
        draft_media_id = "media_id_12345"
        service.add_uploaded_article(article_id, draft_media_id)
        
        # 记录首次上传时间
        first_upload_time = service.get_upload_time(article_id)
        
        # 再次添加相同的记录
        new_draft_media_id = "media_id_67890"
        service.add_uploaded_article(article_id, new_draft_media_id)
        
        # 验证记录没有被覆盖
        assert service.get_upload_count() == 1
        assert service.get_draft_media_id(article_id) == draft_media_id
        assert service.get_upload_time(article_id) == first_upload_time

    def test_load_from_file(self):
        """测试重启后能从文件加载"""
        # 第一次创建服务并添加记录
        service1 = UploadHistoryService(self.temp_file_path)
        article_id = "12345"
        draft_media_id = "media_id_12345"
        service1.add_uploaded_article(article_id, draft_media_id)
        
        # 关闭服务并重新创建
        del service1
        service2 = UploadHistoryService(self.temp_file_path)
        
        # 验证记录已从文件加载
        assert service2.get_upload_count() == 1
        assert service2.is_uploaded(article_id) is True
        assert service2.get_draft_media_id(article_id) == draft_media_id

    def test_remove_article(self):
        """测试移除记录"""
        # 创建服务实例并添加记录
        service = UploadHistoryService(self.temp_file_path)
        article_id = "12345"
        service.add_uploaded_article(article_id)
        
        # 验证记录存在
        assert service.is_uploaded(article_id) is True
        
        # 移除记录
        result = service.remove_uploaded_article(article_id)
        assert result is True
        
        # 验证记录已移除
        assert service.is_uploaded(article_id) is False
        assert service.get_upload_count() == 0
        
        # 尝试移除不存在的记录
        result = service.remove_uploaded_article("99999")
        assert result is False

    def test_clear_all(self):
        """测试清空所有记录"""
        # 创建服务实例并添加多条记录
        service = UploadHistoryService(self.temp_file_path)
        service.add_uploaded_article("12345")
        service.add_uploaded_article("67890")
        
        # 验证记录存在
        assert service.get_upload_count() == 2
        
        # 清空所有记录
        service.clear_all()
        
        # 验证所有记录已清空
        assert service.get_upload_count() == 0
        assert service.get_all_uploaded_articles() == []

    def test_directory_creation(self):
        """测试目录创建功能"""
        # 创建包含子目录的临时文件路径
        temp_dir = tempfile.mkdtemp()
        nested_file_path = os.path.join(temp_dir, "subdir", "upload_history.json")
        
        try:
            # 创建服务实例，应该自动创建目录
            service = UploadHistoryService(nested_file_path)
            
            # 添加记录
            article_id = "12345"
            service.add_uploaded_article(article_id)
            
            # 验证文件已创建
            assert os.path.exists(nested_file_path)
            
            # 验证记录已保存
            with open(nested_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert article_id in data
        finally:
            # 清理临时目录
            import shutil
            shutil.rmtree(temp_dir)