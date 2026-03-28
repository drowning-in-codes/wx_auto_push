import random
import requests
from bs4 import BeautifulSoup
import time
import os



class BaseCrawler:
    def __init__(self, urls, proxy_config=None):
        self.urls = urls
        self.proxy_config = proxy_config or {}
       

    def get_random_url(self):
        return random.choice(self.urls)

    def _get_proxies(self):
        """
        获取代理配置
        """
        if self.proxy_config.get("enabled"):
            return {
                "http": self.proxy_config.get("http_proxy"),
                "https": self.proxy_config.get("https_proxy"),
            }
        # 如果代理未启用，清空环境变量
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""
        return None

    def crawl(self):
        url = self.get_random_url()
        try:
            response = requests.get(
                url, headers=self._get_headers(), proxies=self._get_proxies()
            )
            response.raise_for_status()
            return self.parse(response.text, url)
        except Exception as e:
            print(f"爬取 {url} 失败: {e}")
            return None

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def parse(self, html, url):
        raise NotImplementedError("子类必须实现parse方法")
