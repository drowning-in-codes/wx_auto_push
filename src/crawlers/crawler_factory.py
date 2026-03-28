from .anime_crawler import AnimeCrawler
from .image_crawler import ImageCrawler
from .pixivision_crawler import PixivisionCrawler


class CrawlerFactory:
    @staticmethod
    def create_crawler(crawler_type, urls, proxy_config=None, request_config=None):
        if crawler_type == "anime":
            return AnimeCrawler(urls, proxy_config)
        elif crawler_type == "image":
            return ImageCrawler(urls, proxy_config)
        elif crawler_type == "pixivision":
            return PixivisionCrawler(urls, proxy_config, request_config)
        else:
            raise ValueError(f"不支持的爬虫类型: {crawler_type}")
