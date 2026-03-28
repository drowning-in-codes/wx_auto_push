from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
import requests


class PixivisionCrawler(BaseCrawler):
    def __init__(self, urls, proxy_config=None):
        super().__init__(urls, proxy_config)

    def parse(self, html, url):
        if "c/illustration" in url:
            return self._parse_illustration_list(html, url)
        elif "/a/" in url:
            return self._parse_illustration_detail(html, url)
        else:
            return None

    def _parse_illustration_list(self, html, url):
        """
        解析插画列表页面
        """
        soup = BeautifulSoup(html, "lxml")
        illustration_items = []

        # 解析文章卡片
        for item in soup.select(".article-card"):
            title_element = item.select_one(".article-card__title")
            link_element = item.select_one("a")
            img_element = item.select_one("img")
            tag_elements = item.select(".tag-item")

            if title_element and link_element:
                title = title_element.text.strip()
                detail_url = link_element.get("href")
                # 确保URL是完整的
                if not detail_url.startswith("http"):
                    detail_url = f"https://www.pixivision.net{detail_url}"
                
                tags = [tag.text.strip() for tag in tag_elements]
                image_url = img_element.get("src") if img_element else None

                illustration_items.append({
                    "title": title,
                    "url": detail_url,
                    "image_url": image_url,
                    "tags": tags,
                    "source": "Pixivision"
                })

        return illustration_items

    def _parse_illustration_detail(self, html, url):
        """
        解析插画详情页面
        """
        soup = BeautifulSoup(html, "lxml")
        
        # 获取标题
        title = soup.select_one(".article-header__title").text.strip() if soup.select_one(".article-header__title") else ""
        
        # 获取介绍文字
        content_elements = soup.select(".article-body p")
        content = "\n".join([element.text.strip() for element in content_elements])
        
        # 获取图片
        image_items = []
        for img in soup.select(".article-body img"):
            img_url = img.get("src")
            if img_url:
                # 确保URL是完整的
                if not img_url.startswith("http"):
                    img_url = f"https://www.pixivision.net{img_url}"
                image_items.append(img_url)
        
        # 获取标签
        tag_elements = soup.select(".tag-item")
        tags = [tag.text.strip() for tag in tag_elements]
        
        return {
            "title": title,
            "url": url,
            "content": content,
            "images": image_items,
            "tags": tags,
            "source": "Pixivision"
        }

    def crawl_pages(self, base_url, start_page, end_page):
        """
        爬取多个页面的插画列表
        """
        all_illustrations = []
        
        for page in range(start_page, end_page + 1):
            page_url = f"{base_url}?p={page}"
            try:
                response = requests.get(
                    page_url, headers=self._get_headers(), proxies=self._get_proxies()
                )
                response.raise_for_status()
                page_illustrations = self._parse_illustration_list(response.text, page_url)
                if page_illustrations:
                    all_illustrations.extend(page_illustrations)
            except Exception as e:
                print(f"爬取 {page_url} 失败: {e}")
        
        return all_illustrations
