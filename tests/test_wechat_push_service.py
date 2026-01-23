import pytest
from unittest.mock import MagicMock
from src.push.wechat_push_service import WeChatPushService


class TestWeChatPushService:
    """测试微信推送服务"""

    @pytest.fixture
    def push_service(self):
        """创建推送服务实例，使用mock的配置"""
        # 创建mock的配置
        mock_config = MagicMock()

        # 配置mock的返回值
        mock_config.get_wechat_config.return_value = {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "template_id": "test_template_id",
            "preview": {"towxname": "test_wxname"},
        }

        mock_config.get_proxy_config.return_value = {}
        mock_config.get_push_config.return_value = {"image_publish_type": "image"}

        # 创建推送服务实例
        # 注意：这里会实际创建WeChatClient实例，我们需要通过mock来替换它
        push_service = WeChatPushService(mock_config)

        # 使用mock替换实际的微信客户端
        push_service.client = MagicMock()

        # 使用mock替换实际的素材服务
        push_service.material_service = MagicMock()

        return push_service

    def test_push_text_content(self, push_service):
        """测试推送文本消息"""
        # 配置mock客户端的mass_send_text方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "msg_id": 1234567890,
            "msg_data_id": 1234567890,
        }
        push_service.client.mass_send_text.return_value = expected_result

        # 执行测试
        content = "测试文本内容"
        is_to_all = True
        tag_id = None
        clientmsgid = "test_clientmsgid"
        result = push_service.push_text_content(content, is_to_all, tag_id, clientmsgid)

        # 验证结果
        assert result == expected_result
        push_service.client.mass_send_text.assert_called_once_with(
            content, is_to_all, tag_id, clientmsgid
        )

    def test_push_image_content(self, push_service):
        """测试推送图片消息"""
        # 配置mock素材服务的upload_image_media方法返回值
        mock_upload_result = {
            "media_id": "test_media_id",
            "url": "http://example.com/test.jpg",
        }
        push_service.material_service.upload_image_media.return_value = (
            mock_upload_result
        )

        # 配置mock客户端的mass_send_image方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "msg_id": 1234567890,
            "msg_data_id": 1234567890,
        }
        push_service.client.mass_send_image.return_value = expected_result

        # 执行测试
        image_url = "http://example.com/test.jpg"
        description = "测试图片描述"
        is_to_all = True
        tag_id = None
        clientmsgid = "test_clientmsgid"
        result = push_service.push_image_content(
            image_url, description, is_to_all, tag_id, clientmsgid
        )

        # 验证结果
        assert result == expected_result
        push_service.material_service.upload_image_media.assert_called_once_with(
            image_url
        )
        push_service.client.mass_send_image.assert_called_once_with(
            mock_upload_result["media_id"], is_to_all, tag_id, clientmsgid
        )

    def test_push_news_article(self, push_service):
        """测试推送图文消息"""
        # 配置mock素材服务的upload_news_media方法返回值
        mock_upload_result = {"media_id": "test_news_media_id"}
        push_service.material_service.upload_news_media.return_value = (
            mock_upload_result
        )

        # 配置mock客户端的mass_send_news方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "msg_id": 1234567890,
            "msg_data_id": 1234567890,
        }
        push_service.client.mass_send_news.return_value = expected_result

        # 执行测试
        title = "测试标题"
        content = "测试内容"
        image_url = "http://example.com/test.jpg"
        url = "http://example.com/article"
        is_to_all = True
        tag_id = None
        clientmsgid = "test_clientmsgid"
        send_ignore = False
        result = push_service.push_news_article(
            title, content, image_url, url, is_to_all, tag_id, clientmsgid, send_ignore
        )

        # 验证结果
        assert result == expected_result
        push_service.material_service.upload_news_media.assert_called_once()
        push_service.client.mass_send_news.assert_called_once()

    def test_preview_text_message(self, push_service):
        """测试预览文本消息"""
        # 配置mock客户端的preview_message方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        push_service.client.preview_message.return_value = expected_result

        # 执行测试
        content = "测试预览文本内容"
        towxname = "test_wxname"
        result = push_service.preview_text_message(content, towxname)

        # 验证结果
        assert result == expected_result
        push_service.client.preview_message.assert_called_once_with(
            "text", content, towxname
        )

    def test_preview_image_message(self, push_service):
        """测试预览图片消息"""
        # 配置mock素材服务的upload_image_media方法返回值
        mock_upload_result = {
            "media_id": "test_preview_media_id",
            "url": "http://example.com/preview.jpg",
        }
        push_service.material_service.upload_image_media.return_value = (
            mock_upload_result
        )

        # 配置mock客户端的preview_message方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        push_service.client.preview_message.return_value = expected_result

        # 执行测试
        image_url = "http://example.com/preview.jpg"
        description = "测试预览图片描述"
        towxname = "test_wxname"
        result = push_service.preview_image_message(image_url, description, towxname)

        # 验证结果
        assert result == expected_result
        push_service.material_service.upload_image_media.assert_called_once_with(
            image_url
        )
        push_service.client.preview_message.assert_called_once_with(
            "image", mock_upload_result["media_id"], towxname
        )

    def test_preview_news_message(self, push_service):
        """测试预览图文消息"""
        # 配置mock素材服务的upload_news_media方法返回值
        mock_upload_result = {"media_id": "test_preview_news_media_id"}
        push_service.material_service.upload_news_media.return_value = (
            mock_upload_result
        )

        # 配置mock客户端的preview_message方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        push_service.client.preview_message.return_value = expected_result

        # 执行测试
        title = "测试预览标题"
        content = "测试预览内容"
        image_url = "http://example.com/preview.jpg"
        url = "http://example.com/preview_article"
        towxname = "test_wxname"
        result = push_service.preview_news_message(
            title, content, image_url, url, towxname
        )

        # 验证结果
        assert result == expected_result
        push_service.material_service.upload_news_media.assert_called_once()
        push_service.client.preview_message.assert_called_once_with(
            "mpnews", mock_upload_result["media_id"], towxname
        )

    def test_push_random_content_text(self, push_service):
        """测试推送随机文本内容"""
        # 配置mock客户端的mass_send_text方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "msg_id": 1234567890,
            "msg_data_id": 1234567890,
        }
        push_service.client.mass_send_text.return_value = expected_result

        # 执行测试
        content_list = ["测试文本1", "测试文本2", "测试文本3"]
        result = push_service.push_random_content(content_list)

        # 验证结果
        assert result == expected_result
        push_service.client.mass_send_text.assert_called_once()

    def test_push_random_content_image(self, push_service):
        """测试推送随机图片内容"""
        # 配置mock素材服务的upload_image_media方法返回值
        mock_upload_result = {
            "media_id": "test_media_id",
            "url": "http://example.com/test.jpg",
        }
        push_service.material_service.upload_image_media.return_value = (
            mock_upload_result
        )

        # 配置mock客户端的mass_send_image方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "msg_id": 1234567890,
            "msg_data_id": 1234567890,
        }
        push_service.client.mass_send_image.return_value = expected_result

        # 执行测试
        content_list = [
            {"image_url": "http://example.com/test1.jpg", "description": "测试图片1"},
            {"image_url": "http://example.com/test2.jpg", "description": "测试图片2"},
        ]
        result = push_service.push_random_content(content_list)

        # 验证结果
        assert result == expected_result
        push_service.material_service.upload_image_media.assert_called_once()
        push_service.client.mass_send_image.assert_called_once()

    def test_push_random_content_news(self, push_service):
        """测试推送随机图文内容"""
        # 配置mock素材服务的upload_news_media方法返回值
        mock_upload_result = {"media_id": "test_news_media_id"}
        push_service.material_service.upload_news_media.return_value = (
            mock_upload_result
        )

        # 配置mock客户端的mass_send_news方法返回值
        expected_result = {
            "errcode": 0,
            "errmsg": "ok",
            "msg_id": 1234567890,
            "msg_data_id": 1234567890,
        }
        push_service.client.mass_send_news.return_value = expected_result

        # 执行测试 - 使用没有image_url的内容，确保走图文推送逻辑
        content_list = [
            {
                "title": "测试标题1",
                "content": "测试内容1",
                "url": "http://example.com/article1",
            },
            {
                "title": "测试标题2",
                "content": "测试内容2",
                "url": "http://example.com/article2",
            },
        ]
        result = push_service.push_random_content(content_list)

        # 验证结果
        assert result == expected_result
        push_service.material_service.upload_news_media.assert_called_once()
        push_service.client.mass_send_news.assert_called_once()
