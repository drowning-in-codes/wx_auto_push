import pytest
from unittest.mock import MagicMock
from src.push.wechat_material_service import WeChatMaterialService


class TestWeChatMaterialService:
    """测试微信素材服务"""

    @pytest.fixture
    def material_service(self):
        """创建素材服务实例，使用mock的微信客户端"""
        # 创建mock的微信客户端
        mock_client = MagicMock()
        # 创建素材服务实例
        material_service = WeChatMaterialService(mock_client)
        return material_service, mock_client

    def test_get_material_count(self, material_service):
        """测试获取素材总数"""
        material_service_instance, mock_client = material_service

        # 配置mock客户端的get_material_count方法返回值
        expected_result = {
            "voice_count": 10,
            "video_count": 5,
            "image_count": 20,
            "news_count": 15,
        }
        mock_client.get_material_count.return_value = expected_result

        # 执行测试
        result = material_service_instance.get_material_count()

        # 验证结果
        assert result == expected_result
        mock_client.get_material_count.assert_called_once()

    def test_batch_get_material(self, material_service):
        """测试获取素材列表"""
        material_service_instance, mock_client = material_service

        # 配置mock客户端的batch_get_material方法返回值
        expected_result = {
            "item": [
                {"media_id": "media123", "name": "test.jpg", "update_time": 1620000000}
            ],
            "total_count": 1,
            "item_count": 1,
        }
        mock_client.batch_get_material.return_value = expected_result

        # 执行测试
        material_type = "image"
        offset = 0
        count = 20
        result = material_service_instance.batch_get_material(
            material_type, offset, count
        )

        # 验证结果
        assert result == expected_result
        mock_client.batch_get_material.assert_called_once_with(
            material_type, offset, count
        )

    def test_get_material(self, material_service):
        """测试获取素材"""
        material_service_instance, mock_client = material_service

        # 配置mock客户端的get_material方法返回值
        expected_result = {
            "title": "测试素材",
            "author": "测试作者",
            "content": "测试内容",
        }
        mock_client.get_material.return_value = expected_result

        # 执行测试
        media_id = "media123"
        result = material_service_instance.get_material(media_id)

        # 验证结果
        assert result == expected_result
        mock_client.get_material.assert_called_once_with(media_id)

    def test_add_material(self, material_service):
        """测试新增素材"""
        material_service_instance, mock_client = material_service

        # 配置mock客户端的add_material方法返回值
        expected_result = {"media_id": "media123", "url": "http://example.com/test.jpg"}
        mock_client.add_material.return_value = expected_result

        # 执行测试
        material_type = "image"
        file_path = "/path/to/image.jpg"
        title = "测试图片"
        description = "这是一张测试图片"
        result = material_service_instance.add_material(
            material_type, file_path, title, description
        )

        # 验证结果
        assert result == expected_result
        mock_client.add_material.assert_called_once_with(
            material_type, file_path, title, description
        )

    def test_delete_material(self, material_service):
        """测试删除素材"""
        material_service_instance, mock_client = material_service

        # 配置mock客户端的delete_material方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        mock_client.delete_material.return_value = expected_result

        # 执行测试
        media_id = "media123"
        result = material_service_instance.delete_material(media_id)

        # 验证结果
        assert result == expected_result
        mock_client.delete_material.assert_called_once_with(media_id)

    def test_upload_temporary_material(self, material_service):
        """测试上传临时素材"""
        material_service_instance, mock_client = material_service

        # 配置mock客户端的upload_temp_media方法返回值
        expected_result = {
            "media_id": "temp_media123",
            "type": "image",
            "created_at": 1620000000,
        }
        mock_client.upload_temp_media.return_value = expected_result

        # 执行测试
        material_type = "image"
        file_path = "/path/to/temp_image.jpg"
        result = material_service_instance.upload_temporary_material(
            material_type, file_path
        )

        # 验证结果
        assert result == expected_result
        mock_client.upload_temp_media.assert_called_once_with(material_type, file_path)

    def test_get_temporary_material(self, material_service):
        """测试获取临时素材"""
        material_service_instance, mock_client = material_service
        
        # 配置mock客户端的get_media方法返回值
        expected_result = b"binary_image_data"
        mock_client.get_media.return_value = expected_result
        
        # 执行测试
        media_id = "temp_media123"
        result = material_service_instance.get_temporary_material(media_id)
        
        # 验证结果
        assert result == expected_result
        mock_client.get_media.assert_called_once_with(media_id)

    def test_upload_news_image(self, material_service):
        """测试上传图文消息内图片"""
        material_service_instance, mock_client = material_service
        
        # 配置mock客户端的upload_news_image方法返回值
        expected_result = {
            "url": "http://example.com/news_image.jpg"
        }
        mock_client.upload_news_image.return_value = expected_result
        
        # 执行测试
        image_file = "/path/to/news_image.jpg"
        result = material_service_instance.upload_news_image(image_file)
        
        # 验证结果
        assert result == expected_result
        mock_client.upload_news_image.assert_called_once_with(image_file)

    def test_upload_image_media(self, material_service):
        """测试上传图片到临时素材"""
        material_service_instance, mock_client = material_service
        
        # 配置mock客户端的upload_image_media方法返回值
        expected_result = {
            "media_id": "image_media123",
            "url": "http://example.com/image.jpg"
        }
        mock_client.upload_image_media.return_value = expected_result
        
        # 执行测试
        image_url = "http://example.com/image.jpg"
        result = material_service_instance.upload_image_media(image_url)
        
        # 验证结果
        assert result == expected_result
        mock_client.upload_image_media.assert_called_once_with(image_url)

    def test_upload_news_media(self, material_service):
        """测试上传图文消息素材"""
        material_service_instance, mock_client = material_service
        
        # 配置mock客户端的upload_news_media方法返回值
        expected_result = {
            "media_id": "news_media123"
        }
        mock_client.upload_news_media.return_value = expected_result
        
        # 测试数据
        articles = [
            {
                "title": "测试标题",
                "description": "测试描述",
                "url": "http://example.com/test",
                "picurl": "http://example.com/test.jpg"
            }
        ]
        
        # 执行测试
        result = material_service_instance.upload_news_media(articles)
        
        # 验证结果
        assert result == expected_result
        mock_client.upload_news_media.assert_called_once_with(articles)
