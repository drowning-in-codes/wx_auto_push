from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
import random


class ImageCrawler(BaseCrawler):
    def parse(self, html, url):
        if "pixiv.net" in url:
            return self._parse_pixiv(html)
        elif "wallhaven.cc" in url:
            return self._parse_wallhaven(html)
        elif "unsplash.com" in url:
            return self._parse_unsplash(html)
        elif "pexels.com" in url:
            return self._parse_pexels(html)
        elif "pixivision.net" in url:
            return self._parse_pixivision(html)
        elif "pixibloom.kafuuchino.com.cn" in url:
            return self._parse_pixibloom(html)
        else:
            return self._parse_generic(html)

    def _parse_pixiv(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select(".work"):
            img = item.select_one("img")
            if img:
                image_items.append(
                    {"url": img.get("src"), "alt": img.get("alt"), "source": "Pixiv"}
                )

        return random.choice(image_items) if image_items else None

    def _parse_wallhaven(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select(".thumb"):
            img = item.select_one("img")
            if img:
                image_items.append(
                    {
                        "url": img.get("src"),
                        "alt": img.get("alt"),
                        "source": "Wallhaven",
                    }
                )

        return random.choice(image_items) if image_items else None

    def _parse_unsplash(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select(".photo"):
            img = item.select_one("img")
            if img:
                image_items.append(
                    {"url": img.get("src"), "alt": img.get("alt"), "source": "Unsplash"}
                )

        return random.choice(image_items) if image_items else None

    def _parse_pexels(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select(".photo-item"):
            img = item.select_one("img")
            if img:
                image_items.append(
                    {"url": img.get("src"), "alt": img.get("alt"), "source": "Pexels"}
                )

        return random.choice(image_items) if image_items else None

    def _parse_generic(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select("img"):
            img_url = item.get("src")
            if img_url and (
                img_url.endswith(".jpg")
                or img_url.endswith(".png")
                or img_url.endswith(".gif")
            ):
                image_items.append(
                    {"url": img_url, "alt": item.get("alt", "图片"), "source": "未知"}
                )

        return random.choice(image_items) if image_items else None

    def _parse_pixivision(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select(".article-card"):
            img = item.select_one("img")
            if img:
                image_items.append(
                    {
                        "url": img.get("src"),
                        "alt": img.get("alt"),
                        "source": "Pixivision",
                    }
                )

        return random.choice(image_items) if image_items else None

    def _parse_pixibloom(self, html):
        soup = BeautifulSoup(html, "lxml")
        image_items = []

        for item in soup.select(".image-item"):
            img = item.select_one("img")
            if img:
                image_items.append(
                    {
                        "url": img.get("src"),
                        "alt": img.get("alt", "Pixibloom图片"),
                        "source": "Pixibloom",
                    }
                )

        return random.choice(image_items) if image_items else None
