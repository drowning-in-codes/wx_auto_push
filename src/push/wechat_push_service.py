from .wechat_client import WeChatClient
import random


class WeChatPushService:
    def __init__(self, config):
        wechat_config = config.get_wechat_config()
        self.client = WeChatClient(
            wechat_config.get("app_id"), wechat_config.get("app_secret")
        )
        self.template_id = wechat_config.get("template_id")

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
        upload_result = self.client.upload_image_media(image_url)
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
        upload_result = self.client.upload_news_media(articles)
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
