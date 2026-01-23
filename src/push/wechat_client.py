import requests
import json
import time
import os
from src.utils.cache_manager import CacheManager


class WeChatClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.cache = CacheManager()
        self.access_token = None
        self.token_expire_time = 0

    def get_access_token(self):
        # 尝试从缓存获取
        cached_token = self.cache.get("wechat_access_token")
        if cached_token:
            self.access_token = cached_token["access_token"]
            self.token_expire_time = cached_token["expire_at"]
            return self.access_token

        current_time = time.time()
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url)
        result = response.json()

        if "access_token" in result:
            self.access_token = result["access_token"]
            self.token_expire_time = (
                current_time + result["expires_in"] - 3600
            )  # 提前1小时刷新

            # 存入缓存
            self.cache.set(
                "wechat_access_token",
                {
                    "access_token": self.access_token,
                    "expire_at": self.token_expire_time,
                },
                expire=result["expires_in"] - 3600,
            )

            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")

    def create_menu(self, menu_data):
        access_token = self.get_access_token()
        url = (
            f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
        )
        response = requests.post(url, json=menu_data)
        return response.json()

    def upload_media(self, media_type, media_file):
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}"

        files = {"media": open(media_file, "rb")}

        response = requests.post(url, files=files)
        return response.json()

    def send_article(self, articles):
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"

        data = {
            "touser": "OPENID",  # 这里需要替换为具体的用户OPENID，或者使用模板消息
            "msgtype": "news",
            "news": {"articles": articles},
        }

        response = requests.post(url, json=data)
        return response.json()

    def send_template_message(self, openid, template_id, data, url=None):
        access_token = self.get_access_token()
        api_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"

        template_data = {"touser": openid, "template_id": template_id, "data": data}

        if url:
            template_data["url"] = url

        response = requests.post(api_url, json=template_data)
        return response.json()

    def upload_news_media(self, articles):
        """
        上传图文消息素材，返回media_id
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadnews?access_token={access_token}"

        data = {"articles": articles}
        response = requests.post(url, json=data)
        return response.json()

    def upload_image_media(self, image_url):
        """
        上传图片临时素材，返回media_id
        注意：这里需要先下载图片到本地
        """
        import tempfile
        import shutil

        access_token = self.get_access_token()
        upload_url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"

        # 下载图片到临时文件
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                shutil.copyfileobj(response.raw, temp_file)
                temp_file_path = temp_file.name

            try:
                # 上传图片
                with open(temp_file_path, "rb") as f:
                    files = {"media": f}
                    upload_response = requests.post(upload_url, files=files)
                    return upload_response.json()
            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            raise Exception(f"下载图片失败: {image_url}")

    def upload_news_image(self, image_file):
        """
        上传图文消息内图片，返回图片URL
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"

        files = {"media": open(image_file, "rb")}
        response = requests.post(url, files=files)
        return response.json()

    def preview_message(self, msg_type, content, openid):
        """
        预览消息
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/preview?access_token={access_token}"

        data = {"touser": openid, "msgtype": msg_type}

        if msg_type == "text":
            data["text"] = {"content": content}
        elif msg_type == "image":
            data["image"] = {"media_id": content}
        elif msg_type == "mpnews":
            data["mpnews"] = {"media_id": content}

        response = requests.post(url, json=data)
        return response.json()

    def get_mass_status(self, msg_id):
        """
        查询群发消息发送状态
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/get?access_token={access_token}"

        data = {"msg_id": msg_id}
        response = requests.post(url, json=data)
        return response.json()

    def delete_mass_message(self, msg_id):
        """
        删除群发消息
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/delete?access_token={access_token}"

        data = {"msg_id": msg_id}
        response = requests.post(url, json=data)
        return response.json()

    def mass_send_text(self, content, is_to_all=True, tag_id=None, clientmsgid=None):
        """
        群发文本消息
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}"

        data = {
            "filter": {"is_to_all": is_to_all},
            "text": {"content": content},
            "msgtype": "text",
        }

        if tag_id:
            data["filter"]["is_to_all"] = False
            data["filter"]["tag_id"] = tag_id

        if clientmsgid:
            data["clientmsgid"] = clientmsgid

        response = requests.post(url, json=data)
        return response.json()

    def mass_send_image(self, media_id, is_to_all=True, tag_id=None, clientmsgid=None):
        """
        群发图片消息
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}"

        data = {
            "filter": {"is_to_all": is_to_all},
            "image": {"media_id": media_id},
            "msgtype": "image",
        }

        if tag_id:
            data["filter"]["is_to_all"] = False
            data["filter"]["tag_id"] = tag_id

        if clientmsgid:
            data["clientmsgid"] = clientmsgid

        response = requests.post(url, json=data)
        return response.json()

    def mass_send_news(
        self, media_id, is_to_all=True, tag_id=None, clientmsgid=None, send_ignore=False
    ):
        """
        群发图文消息
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}"

        data = {
            "filter": {"is_to_all": is_to_all},
            "mpnews": {"media_id": media_id},
            "msgtype": "mpnews",
        }

        if tag_id:
            data["filter"]["is_to_all"] = False
            data["filter"]["tag_id"] = tag_id

        if clientmsgid:
            data["clientmsgid"] = clientmsgid

        if send_ignore:
            data["send_ignore"] = send_ignore

        response = requests.post(url, json=data)
        return response.json()

    def mass_send_by_openid(self, msg_type, content, openid_list, clientmsgid=None):
        """
        根据OpenID列表群发消息
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/send?access_token={access_token}"

        data = {
            "touser": openid_list,
            "msgtype": msg_type,
        }

        if msg_type == "text":
            data["text"] = {"content": content}
        elif msg_type == "image":
            data["image"] = {"media_id": content}
        elif msg_type == "mpnews":
            data["mpnews"] = {"media_id": content}

        if clientmsgid:
            data["clientmsgid"] = clientmsgid

        response = requests.post(url, json=data)
        return response.json()
