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
        elif url == "https://www.pixivision.net/zh/":
            # 默认返回排行榜（第一个容器）
            return self._parse_ranking_list(html, url, 0)
        else:
            return None

    def _parse_illustration_list(self, html, url):
        """
        解析插画列表页面
        """
        soup = BeautifulSoup(html, "lxml")
        illustration_items = []

        # 解析文章卡片
        for item in soup.select("._article-card"):
            # 查找标题元素
            title_element = item.select_one(".arc__title a")
            link_element = item.select_one(".arc__thumbnail-container a")

            # 查找图片元素（在背景样式中）
            thumbnail_element = item.select_one("._thumbnail")
            image_url = None
            if thumbnail_element:
                style = thumbnail_element.get("style", "")
                if "background-image" in style:
                    import re

                    match = re.search(r"url\s*\((.*?)\)", style)
                    if match:
                        image_url = match.group(1).strip("\"'")

            # 查找标签元素
            tag_elements = item.select(".tls__list-item")

            if title_element and link_element:
                title = title_element.text.strip()
                detail_url = link_element.get("href")
                # 确保URL是完整的
                if not detail_url.startswith("http"):
                    detail_url = f"https://www.pixivision.net{detail_url}"

                # 提取 article id
                article_id = ""
                import re

                match = re.search(r"/a/(\d+)", detail_url)
                if match:
                    article_id = match.group(1)

                tags = [tag.text.strip() for tag in tag_elements]

                illustration_items.append(
                    {
                        "title": title,
                        "url": detail_url,
                        "article_id": article_id,
                        "image_url": image_url,
                        "tags": tags,
                        "source": "Pixivision",
                    }
                )

        return illustration_items

    def _parse_illustration_detail(self, html, url):
        """
        解析插画详情页面
        """
        soup = BeautifulSoup(html, "lxml")

        # 获取标题
        title = soup.select_one("h1").text.strip() if soup.select_one("h1") else ""

        # 获取介绍文字
        content_elements = soup.select(
            ".article-item._feature-article-body__paragraph p"
        )
        content = "\n".join([element.text.strip() for element in content_elements])

        # 获取图片
        image_items = []

        # 首先获取封面图片
        eyecatch_img = soup.select_one("div._article-illust-eyecatch img.aie__image")
        if eyecatch_img:
            img_url = eyecatch_img.get("src")
            if img_url:
                # 确保URL是完整的
                if not img_url.startswith("http"):
                    img_url = f"https://www.pixivision.net{img_url}"
                image_items.append(img_url)

        # 然后获取插画图片
        for container in soup.select("_clickable-image-container.fit-inner"):
            img = container.select_one("img")
            if img:
                img_url = img.get("src")
                if img_url:
                    # 确保URL是完整的
                    if not img_url.startswith("http"):
                        img_url = f"https://www.pixivision.net{img_url}"
                    image_items.append(img_url)

        # 获取标签
        tag_elements = soup.select(".tls__list-item")
        tags = [tag.text.strip() for tag in tag_elements]

        return {
            "title": title,
            "url": url,
            "content": content,
            "images": image_items,
            "tags": tags,
            "source": "Pixivision",
        }

    def _parse_ranking_list(self, html, url, container_index=0):
        """
        解析排行榜或推荐榜列表
        :param container_index: 侧边栏容器索引，0 表示排行榜（第一个），1 表示推荐榜（第二个）
        """
        soup = BeautifulSoup(html, "lxml")

        illustrations = []

        # 查找所有 sidebar-contents-container
        contents_containers = soup.select(".sidebar-contents-container")
        if contents_containers and container_index < len(contents_containers):
            # 获取指定索引的容器
            target_container = contents_containers[container_index]
            # 查找文章列表卡片
            section = target_container.select_one("._articles-list-card")

            if section:
                # 查找所有列表项
                for item in section.select(".alc__articles-list-item"):
                    # 获取链接
                    link = item.select_one(".asc__title-link")
                    if not link:
                        continue

                    illustration_url = link.get("href")
                    if illustration_url:
                        if not illustration_url.startswith("http"):
                            illustration_url = (
                                f"https://www.pixivision.net{illustration_url}"
                            )

                    # 获取标题
                    title = (
                        link.select_one(".asc__title").text.strip()
                        if link.select_one(".asc__title")
                        else ""
                    )

                    # 获取分类
                    category = ""
                    category_link = item.select_one(".asc__category-link")
                    if category_link:
                        category = category_link.text.strip()

                    # 获取缩略图
                    thumbnail = ""
                    thumbnail_div = item.select_one("._thumbnail")
                    if thumbnail_div:
                        style = thumbnail_div.get("style")
                        if style:
                            # 从 style 中提取背景图片 URL
                            import re

                            match = re.search(r"url\((.*?)\)", style)
                            if match:
                                thumbnail = match.group(1)

                    # 提取文章 ID
                    article_id = ""
                    import re

                    match = re.search(r"/a/(\d+)", illustration_url)
                    if match:
                        article_id = match.group(1)

                    # 根据容器索引设置来源
                    source = (
                        "Pixivision Ranking"
                        if container_index == 0
                        else "Pixivision Recommendations"
                    )

                    illustrations.append(
                        {
                            "title": title,
                            "url": illustration_url,
                            "article_id": article_id,
                            "category": category,
                            "thumbnail": thumbnail,
                            "source": source,
                        }
                    )

        return illustrations

    def crawl_pages(self, base_url, start_page, end_page):
        """
        爬取多个页面的插画列表
        """
        all_illustrations = []

        for page in range(start_page, end_page + 1):
            page_url = f"{base_url}?p={page}"
            try:
                response = self.session.get(
                    page_url, headers=self._get_headers(), proxies=self._get_proxies()
                )
                response.raise_for_status()
                page_illustrations = self._parse_illustration_list(
                    response.text, page_url
                )
                if page_illustrations:
                    all_illustrations.extend(page_illustrations)
            except Exception as e:
                print(f"爬取 {page_url} 失败: {e}")

        return all_illustrations
