from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
import re


class AnimeCrawler(BaseCrawler):
    def parse(self, html, url):
        if "dmzj.com" in url:
            return self._parse_dmzj(html)
        elif "acfun.cn" in url:
            return self._parse_acfun(html)
        elif "bilibili.com" in url:
            return self._parse_bilibili(html)
        elif "iqiyi.com" in url:
            return self._parse_iqiyi(html)
        elif "gamersky.com" in url:
            return self._parse_gamersky(html)
        elif "3dmgame.com" in url:
            return self._parse_3dmgame(html)
        else:
            return self._parse_generic(html)

    def _parse_dmzj(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select(".news_list li"):
            title = item.select_one(".title a")
            if title:
                news_items.append(
                    {
                        "title": title.text.strip(),
                        "url": title.get("href"),
                        "source": "动漫之家",
                    }
                )

        return random.choice(news_items) if news_items else None

    def _parse_acfun(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select(".article-list-item"):
            title = item.select_one(".title")
            if title:
                news_items.append(
                    {
                        "title": title.text.strip(),
                        "url": item.get("href"),
                        "source": "AcFun",
                    }
                )

        return random.choice(news_items) if news_items else None

    def _parse_bilibili(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select(".bangumi-item"):
            title = item.select_one(".bangumi-title")
            if title:
                news_items.append(
                    {
                        "title": title.text.strip(),
                        "url": item.get("href"),
                        "source": "哔哩哔哩",
                    }
                )

        return random.choice(news_items) if news_items else None

    def _parse_iqiyi(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select(".site-piclist_pic"):
            title = item.get("alt")
            if title:
                news_items.append(
                    {
                        "title": title.strip(),
                        "url": item.get("href"),
                        "source": "爱奇艺",
                    }
                )

        return random.choice(news_items) if news_items else None

    def _parse_generic(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select("a"):
            title = item.text.strip()
            url = item.get("href")
            if title and url and len(title) > 5:
                news_items.append({"title": title, "url": url, "source": "未知"})

        return random.choice(news_items) if news_items else None

    def _parse_gamersky(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select(".news_list li"):
            title = item.select_one("a")
            if title:
                news_items.append(
                    {
                        "title": title.text.strip(),
                        "url": title.get("href"),
                        "source": "游民星空ACG",
                    }
                )

        return random.choice(news_items) if news_items else None

    def _parse_3dmgame(self, html):
        soup = BeautifulSoup(html, "lxml")
        news_items = []

        for item in soup.select(".list_con li"):
            title = item.select_one("a")
            if title:
                news_items.append(
                    {
                        "title": title.text.strip(),
                        "url": title.get("href"),
                        "source": "3DM游戏网动漫",
                    }
                )

        return random.choice(news_items) if news_items else None
