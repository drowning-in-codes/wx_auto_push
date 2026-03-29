#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试微信公众号新增草稿API
文档地址: https://developers.weixin.qq.com/doc/subscription/api/draftbox/draftmanage/api_draft_add.html
"""

import requests
import json
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import Config


class WeChatDraftTest:
    def __init__(self, app_id, app_secret, proxy_config=None):
        """
        初始化测试类
        :param app_id: 公众号AppID
        :param app_secret: 公众号AppSecret
        :param proxy_config: 代理配置
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy_config = proxy_config or {}
        self.access_token = None
        self.token_expire_time = 0

        # 根据代理配置设置环境变量
        self._setup_proxy()

    def _setup_proxy(self):
        """
        根据代理配置设置环境变量
        """
        if self.proxy_config.get("enabled"):
            # 启用代理
            http_proxy = self.proxy_config.get("http_proxy", "")
            https_proxy = self.proxy_config.get("https_proxy", "")
            os.environ["HTTP_PROXY"] = http_proxy
            os.environ["HTTPS_PROXY"] = https_proxy
            print(f"启用代理: HTTP={http_proxy}, HTTPS={https_proxy}")
        else:
            # 禁用代理，覆盖系统环境中的代理配置
            os.environ["HTTP_PROXY"] = ""
            os.environ["HTTPS_PROXY"] = ""
            print("禁用代理，覆盖系统代理配置")

    def get_proxies(self):
        """
        获取代理配置
        :return: 代理配置字典
        """
        if self.proxy_config.get("enabled"):
            return {
                "http": self.proxy_config.get("http_proxy"),
                "https": self.proxy_config.get("https_proxy"),
            }
        return None

    def get_access_token(self):
        """
        获取access_token
        :return: access_token
        """
        current_time = int(time.time())

        # 如果token未过期，直接返回
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token

        # 重新获取token
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        try:
            response = requests.get(url, timeout=10, proxies=self.get_proxies())
            result = response.json()

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expire_time = (
                    current_time + result.get("expires_in", 7200) - 300
                )  # 提前5分钟过期
                print(f"获取access_token成功: {self.access_token}")
                return self.access_token
            else:
                print(f"获取access_token失败: {result}")
                return None
        except Exception as e:
            print(f"获取access_token异常: {e}")
            return None

    def create_draft(self, articles):
        """
        新增草稿
        :param articles: 图文素材集合
        :return: API响应结果
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

        payload = {"articles": articles}

        try:
            # 手动序列化JSON，确保中文字符不被转义
            json_payload = json.dumps(payload, ensure_ascii=False)
            response = requests.post(
                url,
                data=json_payload.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                timeout=30,
                proxies=self.get_proxies(),
            )
            result = response.json()

            if "media_id" in result:
                print("创建草稿成功！")
                print(f"Media ID: {result.get('media_id')}")
            else:
                print(f"创建草稿失败: {result}")

            return result
        except Exception as e:
            print(f"创建草稿异常: {e}")
            return None

    def test_news_draft(self):
        """
        测试创建图文消息草稿
        """
        print("\n=== 测试创建图文消息草稿 ===")

        articles = [
            {
                "title": "测试",  # 不超过32个字符
                "author": "proanimer",  # 不超过16个字符
                "digest": "这是图文消息的摘要，不超过128个字符",
                "content": "这是图文消息的具体内容",
                "thumb_media_id": "",  # 需要替换为实际的永久素材ID
                "show_cover_pic": 1,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]

        return self.create_draft(articles)

    def test_newspic_draft(self):
        """
        测试创建图片消息草稿
        """
        print("\n=== 测试创建图片消息草稿 ===")

        articles = [
            {
                "article_type": "newspic",
                "title": "插画",  # 不超过32个字符
                "author": "测试",  # 不超过16个字符
                "digest": "这是图片消息的摘要，不超过128个字符",
                "content": "这是图片消息的内容",
                "image_info": {
                    "image_list": [
                        {"image_media_id": ""},  # 需要替换为实际的永久素材ID
                        {"image_media_id": ""},  # 需要替换为实际的永久素材ID
                    ]
                },
            }
        ]

        return self.create_draft(articles)


if __name__ == "__main__":
    # 从配置文件加载AppID和AppSecret
    config = Config()
    wechat_config = config.get("wechat", {})
    proxy_config = config.get("proxy", {})

    APP_ID = wechat_config.get("app_id", "")
    APP_SECRET = wechat_config.get("app_secret", "")

    if not APP_ID or not APP_SECRET:
        print("错误：请在配置文件中设置微信公众号的app_id和app_secret")
        print("配置文件路径：config.development.json 或 config.production.json")
        sys.exit(1)

    print(f"从配置文件加载AppID: {APP_ID}")

    test = WeChatDraftTest(APP_ID, APP_SECRET, proxy_config)

    # 测试创建图文消息草稿
    # test.test_news_draft()

    # 测试创建图片消息草稿
    test.test_newspic_draft()
