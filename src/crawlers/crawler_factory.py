from .anime_crawler import AnimeCrawler
from .image_crawler import ImageCrawler


class CrawlerFactory:
    @staticmethod
    def create_crawler(crawler_type, urls):
        if crawler_type == "anime":
            return AnimeCrawler(urls)
        elif crawler_type == "image":
            return ImageCrawler(urls)
        else:
            raise ValueError(f"不支持的爬虫类型: {crawler_type}")
