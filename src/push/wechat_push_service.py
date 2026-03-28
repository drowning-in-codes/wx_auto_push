from .wechat_client import WeChatClient
from .wechat_menu_service import WeChatMenuService
from .wechat_material_service import WeChatMaterialService
from .wechat_publish_service import WeChatPublishService
from .wechat_draft_service import WeChatDraftService
import random


class WeChatPushService:
    def __init__(self, config):
        wechat_config = config.get_wechat_config()
        proxy_config = config.get_proxy_config()
        push_config = config.get_push_config()
        self.client = WeChatClient(
            wechat_config.get("app_id"), wechat_config.get("app_secret"), proxy_config
        )
        self.template_id = wechat_config.get("template_id")
        self.preview_config = wechat_config.get("preview", {})
        self.image_publish_type = push_config.get(
            "image_publish_type", "image"
        )  # 默认发布为图片消息

        # 初始化各子服务
        self.menu_service = WeChatMenuService(self.client)
        self.material_service = WeChatMaterialService(self.client)
        self.publish_service = WeChatPublishService(self.client)
        self.draft_service = WeChatDraftService(self.client)

    def push_text_content(self, content, is_to_all=True, tag_id=None, clientmsgid=None):
        """
        群发文本消息
        """
        return self.client.mass_send_text(content, is_to_all, tag_id, clientmsgid)

    def push_image_content(
        self, image_url, description, is_to_all=True, tag_id=None, clientmsgid=None
    ):
        """
        群发图片消息
        """
        # 上传图片获取media_id
        upload_result = self.material_service.upload_image_media(image_url)
        if "media_id" in upload_result:
            media_id = upload_result["media_id"]
            return self.client.mass_send_image(media_id, is_to_all, tag_id, clientmsgid)
        else:
            raise Exception(f"上传图片失败: {upload_result}")

    def push_news_article(
        self,
        title,
        content,
        image_url,
        url,
        is_to_all=True,
        tag_id=None,
        clientmsgid=None,
        send_ignore=False,
    ):
        """
        群发图文消息
        """
        # 准备图文消息素材
        articles = [
            {
                "title": title,
                "description": content[:100] + "..." if len(content) > 100 else content,
                "url": url,
                "picurl": image_url,
                "thumb_media_id": "",  # 可选，缩略图media_id
                "author": "微信公众号",  # 可选，作者
                "content_source_url": url,  # 可选，原文链接
            }
        ]

        # 上传图文消息素材获取media_id
        upload_result = self.material_service.upload_news_media(articles)
        if "media_id" in upload_result:
            media_id = upload_result["media_id"]
            return self.client.mass_send_news(
                media_id, is_to_all, tag_id, clientmsgid, send_ignore
            )
        else:
            raise Exception(f"上传图文消息素材失败: {upload_result}")

    def push_random_content(
        self,
        content_list,
        is_to_all=True,
        tag_id=None,
        clientmsgid=None,
        send_ignore=False,
    ):
        content = random.choice(content_list)

        if isinstance(content, dict):
            if "image_url" in content:
                # 根据配置决定图片发布方式
                if self.image_publish_type == "news":
                    # 发布为图文消息
                    return self.push_news_article(
                        content.get("title", "图片分享"),
                        content.get("description", "分享一张图片"),
                        content["image_url"],
                        content.get("url", ""),
                        is_to_all,
                        tag_id,
                        clientmsgid,
                        send_ignore,
                    )
                else:
                    # 默认发布为图片消息
                    return self.push_image_content(
                        content["image_url"],
                        content.get("description", ""),
                        is_to_all,
                        tag_id,
                        clientmsgid,
                    )
            elif "title" in content and "content" in content:
                return self.push_news_article(
                    content["title"],
                    content["content"],
                    content.get("image_url", ""),
                    content.get("url", ""),
                    is_to_all,
                    tag_id,
                    clientmsgid,
                    send_ignore,
                )
            else:
                return self.push_text_content(
                    str(content), is_to_all, tag_id, clientmsgid
                )
        else:
            return self.push_text_content(str(content), is_to_all, tag_id, clientmsgid)

    def preview_text_message(self, content, towxname=None):
        """
        预览文本消息
        """
        if not towxname:
            towxname = self.preview_config.get("towxname")
        if not towxname:
            raise Exception("未配置预览接收者的微信号")

        # 调用微信客户端的预览方法
        return self.client.preview_message("text", content, towxname)

    def preview_image_message(self, image_url, description, towxname=None):
        """
        预览图片消息
        """
        if not towxname:
            towxname = self.preview_config.get("towxname")
        if not towxname:
            raise Exception("未配置预览接收者的微信号")

        # 上传图片获取media_id
        upload_result = self.material_service.upload_image_media(image_url)
        if "media_id" in upload_result:
            media_id = upload_result["media_id"]
            return self.client.preview_message("image", media_id, towxname)
        else:
            raise Exception(f"上传图片失败: {upload_result}")

    def preview_news_message(self, title, content, image_url, url, towxname=None):
        """
        预览图文消息
        """
        if not towxname:
            towxname = self.preview_config.get("towxname")
        if not towxname:
            raise Exception("未配置预览接收者的微信号")

        # 准备图文消息素材
        articles = [
            {
                "title": title,
                "description": content[:100] + "..." if len(content) > 100 else content,
                "url": url,
                "picurl": image_url,
                "thumb_media_id": "",  # 可选，缩略图media_id
                "author": "微信公众号",  # 可选，作者
                "content_source_url": url,  # 可选，原文链接
            }
        ]

        # 上传图文消息素材获取media_id
        upload_result = self.material_service.upload_news_media(articles)
        if "media_id" in upload_result:
            media_id = upload_result["media_id"]
            return self.client.preview_message("mpnews", media_id, towxname)
        else:
            raise Exception(f"上传图文消息素材失败: {upload_result}")

    def send_image_message(self, image_path):
        """
        发送本地图片消息
        """
        # 上传本地图片获取media_id
        upload_result = self.material_service.upload_local_image_media(image_path)
        if "media_id" in upload_result:
            media_id = upload_result["media_id"]
            return self.client.mass_send_image(media_id)
        else:
            raise Exception(f"上传图片失败: {upload_result}")

    def send_image_message_from_url(self, image_url):
        """
        从URL发送图片消息
        """
        # 上传网络图片获取media_id
        upload_result = self.material_service.upload_image_media(image_url)
        if "media_id" in upload_result:
            media_id = upload_result["media_id"]
            return self.client.mass_send_image(media_id)
        else:
            raise Exception(f"上传图片失败: {upload_result}")

    def send_text_message(self, content):
        """
        发送文本消息
        """
        return self.client.mass_send_text(content)
