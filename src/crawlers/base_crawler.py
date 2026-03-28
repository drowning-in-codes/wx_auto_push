import random
import requests
from bs4 import BeautifulSoup


class BaseCrawler:
    def __init__(self, urls, proxy_config=None):
        self.urls = urls
        self.proxy_config = proxy_config or {}
        # 创建 Session 并配置代理设置
        self.session = requests.Session()
        # 如果代理未启用，禁用系统环境变量中的代理设置
        if not self.proxy_config.get("enabled"):
            self.session.trust_env = False

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
        return None

    def crawl(self):
        url = self.get_random_url()
        try:
            response = self.session.get(
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
