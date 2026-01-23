import pytest
from unittest.mock import MagicMock
from src.push.wechat_publish_service import WeChatPublishService


class TestWeChatPublishService:
    """测试微信发布服务"""

    @pytest.fixture
    def publish_service(self):
        """创建发布服务实例，使用mock的微信客户端"""
        # 创建mock的微信客户端
        mock_client = MagicMock()
        # 创建发布服务实例
        publish_service = WeChatPublishService(mock_client)
        return publish_service, mock_client

    def test_get_published_news_list(self, publish_service):
        """测试获取已发布的消息列表"""
        publish_service_instance, mock_client = publish_service
        
        # 配置mock客户端的get_published_news_list方法返回值
        expected_result = {
            "total_count": 5,
            "item_count": 2,
            "item": [
                {
                    "article_id": "article123",
                    "update_time": 1620000000
                },
                {
                    "article_id": "article456",
                    "update_time": 1620000001
                }
            ]
        }
        mock_client.get_published_news_list.return_value = expected_result
        
        # 执行测试
        offset = 0
        count = 2
        no_content = 0
        result = publish_service_instance.get_published_news_list(offset, count, no_content)
        
        # 验证结果
        assert result == expected_result
        mock_client.get_published_news_list.assert_called_once_with(offset, count, no_content)

    def test_get_published_article(self, publish_service):
        """测试获取已发布的图文信息"""
        publish_service_instance, mock_client = publish_service
        
        # 配置mock客户端的get_published_article方法返回值
        expected_result = {
            "news_item": [
                {
                    "title": "测试文章",
                    "author": "测试作者",
                    "digest": "测试摘要",
                    "content": "测试内容",
                    "content_source_url": "http://example.com/test",
                    "thumb_media_id": "thumb123",
                    "thumb_url": "http://example.com/thumb.jpg",
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                    "url": "http://example.com/article",
                    "is_deleted": False
                }
            ]
        }
        mock_client.get_published_article.return_value = expected_result
        
        # 执行测试
        article_id = "article123"
        result = publish_service_instance.get_published_article(article_id)
        
        # 验证结果
        assert result == expected_result
        mock_client.get_published_article.assert_called_once_with(article_id)

    def test_delete_published_article(self, publish_service):
        """测试删除发布文章"""
        publish_service_instance, mock_client = publish_service
        
        # 配置mock客户端的delete_published_article方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        mock_client.delete_published_article.return_value = expected_result
        
        # 执行测试
        article_id = "article123"
        index = 1
        result = publish_service_instance.delete_published_article(article_id, index)
        
        # 验证结果
        assert result == expected_result
        mock_client.delete_published_article.assert_called_once_with(article_id, index)

    def test_get_publish_status(self, publish_service):
        """测试发布状态查询"""
        publish_service_instance, mock_client = publish_service
        
        # 配置mock客户端的get_publish_status方法返回值
        expected_result = {
            "publish_id": "publish123",
            "publish_status": 0,
            "article_id": "article123",
            "article_detail": {
                "count": 1,
                "item": [
                    {
                        "idx": 1,
                        "article_url": "http://example.com/article"
                    }
                ]
            }
        }
        mock_client.get_publish_status.return_value = expected_result
        
        # 执行测试
        publish_id = "publish123"
        result = publish_service_instance.get_publish_status(publish_id)
        
        # 验证结果
        assert result == expected_result
        mock_client.get_publish_status.assert_called_once_with(publish_id)

    def test_submit_publish(self, publish_service):
        """测试发布草稿"""
        publish_service_instance, mock_client = publish_service
        
        # 配置mock客户端的submit_publish方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "publish_id": "publish123",
            "msg_data_id": "msg123"
        }
        mock_client.submit_publish.return_value = expected_result
        
        # 执行测试
        media_id = "media123"
        result = publish_service_instance.submit_publish(media_id)
        
        # 验证结果
        assert result == expected_result
        mock_client.submit_publish.assert_called_once_with(media_id)
