from .wechat_client import WeChatClient


class WeChatDraftService:
    def __init__(self, client):
        self.client = client

    def draft_switch(self, checkonly=0):
        """
        草稿箱开关设置
        """
        return self.client.draft_switch(checkonly)

    def draft_add(self, articles):
        """
        新增草稿
        """
        return self.client.draft_add(articles)

    def draft_batchget(self, offset=0, count=10, no_content=0):
        """
        获取草稿列表
        """
        return self.client.draft_batchget(offset, count, no_content)

    def draft_count(self):
        """
        获取草稿的总数
        """
        return self.client.draft_count()

    def draft_delete(self, media_id):
        """
        删除草稿
        """
        return self.client.draft_delete(media_id)

    def get_draft(self, media_id):
        """
        获取草稿详情
        """
        return self.client.get_draft(media_id)

    def draft_update(self, media_id, index, articles):
        """
        更新草稿
        """
        return self.client.draft_update(media_id, index, articles)

    def draft_submit(self, media_id, title):
        """
        发布草稿
        """
        return self.client.draft_submit(media_id, title)
