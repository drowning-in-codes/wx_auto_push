import random
import requests
from bs4 import BeautifulSoup


class BaseCrawler:
    def __init__(self, urls):
        self.urls = urls

    def get_random_url(self):
        return random.choice(self.urls)

    def crawl(self):
        url = self.get_random_url()
        try:
            response = requests.get(url, headers=self._get_headers())
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
