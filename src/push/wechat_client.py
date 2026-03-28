import requests
import json
import time
import os
from src.utils.cache_manager import CacheManager


class WeChatClient:
    def __init__(self, app_id, app_secret, proxy_config=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.cache = CacheManager()
        self.access_token = None
        self.token_expire_time = 0
        self.base_url = "https://api.weixin.qq.com"
        self.proxy_config = proxy_config or {}

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

        url = f"{self.base_url}/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = self._request("GET", url)
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

    def _request(self, method, url, **kwargs):
        """
        统一请求发送方法，用于处理所有微信API请求
        """
        # 请求拦截：处理cgi-bin/message/mass/sendall请求
        if "/cgi-bin/message/mass/sendall" in url and method == "POST":
            # 获取请求数据
            data = kwargs.get("json", {})

            # 检查是否是图文消息
            if data.get("msgtype") == "mpnews":
                # 如果没有send_ignore_reprint参数，默认设置为1
                if "send_ignore_reprint" not in data:
                    data["send_ignore_reprint"] = 1
                kwargs["json"] = data

        # 处理代理配置
        proxies = None
        if self.proxy_config.get("enabled"):
            proxies = {
                "http": self.proxy_config.get("http_proxy"),
                "https": self.proxy_config.get("https_proxy"),
            }
        kwargs["proxies"] = proxies

        # 发送请求
        response = requests.request(method, url, **kwargs)
        return response

    def create_menu(self, menu_data):
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/create?access_token={access_token}"
        response = self._request("POST", url, json=menu_data)
        return response.json()

    def upload_media(self, media_type, media_file):
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/media/upload?access_token={access_token}&type={media_type}"

        files = {"media": open(media_file, "rb")}

        response = self._request("POST", url, files=files)
        return response.json()

    def send_article(self, articles):
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/message/custom/send?access_token={access_token}"

        data = {
            "touser": "OPENID",  # 这里需要替换为具体的用户OPENID，或者使用模板消息
            "msgtype": "news",
            "news": {"articles": articles},
        }

        response = self._request("POST", url, json=data)
        return response.json()

    def send_template_message(self, openid, template_id, data, url=None):
        access_token = self.get_access_token()
        api_url = (
            f"{self.base_url}/cgi-bin/message/template/send?access_token={access_token}"
        )

        template_data = {"touser": openid, "template_id": template_id, "data": data}

        if url:
            template_data["url"] = url

        response = self._request("POST", api_url, json=template_data)
        return response.json()

    def upload_news_media(self, articles):
        """
        上传图文消息素材，返回media_id
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/media/uploadnews?access_token={access_token}"

        data = {"articles": articles}
        response = self._request("POST", url, json=data)
        return response.json()

    def upload_image_media(self, image_url):
        """
        上传图片临时素材，返回media_id
        注意：这里需要先下载图片到本地
        """
        import tempfile
        import shutil

        access_token = self.get_access_token()
        upload_url = f"{self.base_url}/cgi-bin/media/upload?access_token={access_token}&type=image"

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
                    upload_response = self._request("POST", upload_url, files=files)
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
        注意：该接口所上传的图片，不占用公众号的素材库中图片数量的100000个的限制
             图片仅支持jpg/png格式，大小必须在1MB以下
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/media/uploadimg?access_token={access_token}"

        with open(image_file, "rb") as f:
            files = {"media": f}
            response = self._request("POST", url, files=files)
            return response.json()

    def upload_news_image_from_url(self, image_url):
        """
        从URL下载图片并上传到图文消息内图片接口，返回图片URL
        注意：该接口所上传的图片，不占用公众号的素材库中图片数量的100000个的限制
             图片仅支持jpg/png格式，大小必须在1MB以下
        """
        import tempfile
        import shutil

        access_token = self.get_access_token()
        upload_url = f"{self.base_url}/cgi-bin/media/uploadimg?access_token={access_token}"

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
                    upload_response = self._request("POST", upload_url, files=files)
                    return upload_response.json()
            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            raise Exception(f"下载图片失败: {image_url}")

    def preview_message(self, msg_type, content, openid):
        """
        预览消息
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/message/mass/preview?access_token={access_token}"
        )

        data = {"touser": openid, "msgtype": msg_type}

        if msg_type == "text":
            data["text"] = {"content": content}
        elif msg_type == "image":
            data["image"] = {"media_id": content}
        elif msg_type == "mpnews":
            data["mpnews"] = {"media_id": content}

        response = self._request("POST", url, json=data)
        return response.json()

    def get_mass_status(self, msg_id):
        """
        查询群发消息发送状态
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/message/mass/get?access_token={access_token}"

        data = {"msg_id": msg_id}
        response = self._request("POST", url, json=data)
        return response.json()

    def delete_mass_message(self, msg_id):
        """
        删除群发消息
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/message/mass/delete?access_token={access_token}"

        data = {"msg_id": msg_id}
        response = self._request("POST", url, json=data)
        return response.json()

    def mass_send_text(self, content, is_to_all=True, tag_id=None, clientmsgid=None):
        """
        群发文本消息
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/message/mass/sendall?access_token={access_token}"
        )

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

        response = self._request("POST", url, json=data)
        return response.json()

    def mass_send_image(self, media_id, is_to_all=True, tag_id=None, clientmsgid=None):
        """
        群发图片消息
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/message/mass/sendall?access_token={access_token}"
        )

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

        response = self._request("POST", url, json=data)
        return response.json()

    def mass_send_news(
        self, media_id, is_to_all=True, tag_id=None, clientmsgid=None, send_ignore=False
    ):
        """
        群发图文消息
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/message/mass/sendall?access_token={access_token}"
        )

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

        # 注意：这里的参数名已经改为send_ignore_reprint，根据微信文档
        if send_ignore:
            data["send_ignore_reprint"] = 1

        response = self._request("POST", url, json=data)
        return response.json()

    def mass_send_by_openid(self, msg_type, content, openid_list, clientmsgid=None):
        """
        根据OpenID列表群发消息
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/message/mass/send?access_token={access_token}"

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
            # 如果是图文消息，默认添加send_ignore_reprint=1
            if "send_ignore_reprint" not in data:
                data["send_ignore_reprint"] = 1

        if clientmsgid:
            data["clientmsgid"] = clientmsgid

        response = self._request("POST", url, json=data)
        return response.json()

    # 自定义菜单相关方法
    def create_menu(self, menu_data):
        """
        创建自定义菜单
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/create?access_token={access_token}"
        response = self._request("POST", url, json=menu_data)
        return response.json()

    def get_current_selfmenu_info(self):
        """
        查询自定义菜单信息
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/get_current_selfmenu_info?access_token={access_token}"
        response = self._request("GET", url)
        return response.json()

    def get_menu(self):
        """
        获取自定义菜单配置
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/get?access_token={access_token}"
        response = self._request("GET", url)
        return response.json()

    def delete_menu(self):
        """
        删除自定义菜单
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/delete?access_token={access_token}"
        response = self._request("GET", url)
        return response.json()

    def create_conditional_menu(self, menu_data):
        """
        创建个性化菜单
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/addconditional?access_token={access_token}"
        response = self._request("POST", url, json=menu_data)
        return response.json()

    def delete_conditional_menu(self, menu_id):
        """
        删除个性化菜单
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/delconditional?access_token={access_token}"
        data = {"menuid": menu_id}
        response = self._request("POST", url, json=data)
        return response.json()

    def try_match_menu(self, user_id):
        """
        测试个性化菜单匹配结果
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/menu/trymatch?access_token={access_token}"
        data = {"user_id": user_id}
        response = self._request("POST", url, json=data)
        return response.json()

    # 永久素材相关方法
    def get_material_count(self):
        """
        获取永久素材总数
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/material/get_materialcount?access_token={access_token}"
        response = self._request("GET", url)
        return response.json()

    def get_material(self, media_id):
        """
        获取永久素材
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/material/get_material?access_token={access_token}"
        )
        data = {"media_id": media_id}
        response = self._request("POST", url, json=data)
        return response.json()

    def add_material(self, material_type, media_file, title=None, introduction=None):
        """
        上传永久素材
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/material/add_material?access_token={access_token}&type={material_type}"

        files = {"media": open(media_file, "rb")}

        data = {}
        if title or introduction:
            data["description"] = {}
            if title:
                data["description"]["title"] = title
            if introduction:
                data["description"]["introduction"] = introduction

        response = self._request("POST", url, files=files, data=data)
        return response.json()

    def delete_material(self, media_id):
        """
        删除永久素材
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/material/del_material?access_token={access_token}"
        )
        data = {"media_id": media_id}
        response = self._request("POST", url, json=data)
        return response.json()

    # 临时素材相关方法
    def get_media(self, media_id):
        """
        获取临时素材
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/media/get?access_token={access_token}&media_id={media_id}"
        response = self._request("GET", url)
        return response.json()

    def upload_temp_media(self, material_type, media_file):
        """
        上传临时素材
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/media/upload?access_token={access_token}&type={material_type}"

        files = {"media": open(media_file, "rb")}
        response = self._request("POST", url, files=files)
        return response.json()

    def get_hd_voice(self, media_id):
        """
        获取高清语音素材
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/media/get/jssdk?access_token={access_token}&media_id={media_id}"
        response = self._request("GET", url)
        return response.json()

    # 发布相关方法
    def get_published_news_list(self, offset=0, count=10, no_content=0):
        """
        获取已发布的消息列表
        """
        access_token = self.get_access_token()
        url = (
            f"{self.base_url}/cgi-bin/freepublish/batchget?access_token={access_token}"
        )
        data = {"offset": offset, "count": count, "no_content": no_content}
        response = self._request("POST", url, json=data)
        return response.json()

    def get_published_article(self, article_id):
        """
        获取已发布的图文信息
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/freepublish/getarticle?access_token={access_token}"
        data = {"article_id": article_id}
        response = self._request("POST", url, json=data)
        return response.json()

    def delete_published_article(self, article_id, index=0):
        """
        删除发布文章
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/freepublish/delete?access_token={access_token}"
        data = {"article_id": article_id, "index": index}
        response = self._request("POST", url, json=data)
        return response.json()

    def get_publish_status(self, publish_id):
        """
        发布状态查询
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/freepublish/get?access_token={access_token}"
        data = {"publish_id": publish_id}
        response = self._request("POST", url, json=data)
        return response.json()

    def submit_publish(self, media_id):
        """
        发布草稿
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/cgi-bin/freepublish/submit?access_token={access_token}"
        data = {"media_id": media_id}
        response = self._request("POST", url, json=data)
        return response.json()
