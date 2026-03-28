from .wechat_client import WeChatClient


class WeChatMaterialService:
    def __init__(self, client):
        """
        初始化微信素材服务
        :param client: WeChatClient实例
        """
        self.client = client

    def get_material_count(self):
        """
        获取永久素材总数
        """
        return self.client.get_material_count()

    def batch_get_material(self, material_type, offset=0, count=20):
        """
        获取永久素材列表
        """
        return self.client.batch_get_material(material_type, offset, count)

    def get_material(self, media_id):
        """
        获取永久素材
        """
        return self.client.get_material(media_id)

    def add_material(self, material_type, media_file, title=None, description=None):
        """
        新增永久素材
        """
        return self.client.add_material(material_type, media_file, title, description)

    def delete_material(self, media_id):
        """
        删除永久素材
        """
        return self.client.delete_material(media_id)

    def upload_temporary_material(self, material_type, media_file):
        """
        上传临时素材
        """
        return self.client.upload_temp_media(material_type, media_file)

    def get_temporary_material(self, media_id):
        """
        获取临时素材
        """
        return self.client.get_temporary_material(media_id)

    def upload_news_image(self, image_file):
        """
        上传图文消息内图片
        """
        return self.client.upload_news_image(image_file)

    def upload_news_image_from_url(self, image_url):
        """
        从URL下载图片并上传到图文消息内图片接口
        """
        return self.client.upload_news_image_from_url(image_url)

    def upload_image_media(self, image_url):
        """
        上传图片到临时素材
        """
        return self.client.upload_image_media(image_url)

    def upload_news_media(self, articles):
        """
        上传图文消息素材
        """
        return self.client.upload_news_media(articles)

    def upload_local_image_media(self, image_path):
        """
        上传本地图片到临时素材
        """
        return self.client.upload_temp_media("image", image_path)
