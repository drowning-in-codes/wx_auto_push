from .wechat_client import WeChatClient


class WeChatPublishService:
    def __init__(self, client):
        """
        初始化微信发布服务
        :param client: WeChatClient实例
        """
        self.client = client

    def get_published_news_list(self, offset=0, count=10, no_content=0):
        """
        获取已发布的消息列表
        """
        return self.client.get_published_news_list(offset, count, no_content)

    def get_published_article(self, article_id):
        """
        获取已发布的图文信息
        """
        return self.client.get_published_article(article_id)

    def delete_published_article(self, article_id, index=0):
        """
        删除发布文章
        """
        return self.client.delete_published_article(article_id, index)

    def get_publish_status(self, publish_id):
        """
        发布状态查询
        """
        return self.client.get_publish_status(publish_id)

    def submit_publish(self, media_id):
        """
        发布草稿
        """
        return self.client.submit_publish(media_id)
