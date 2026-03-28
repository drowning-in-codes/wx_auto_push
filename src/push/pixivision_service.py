from src.crawlers.crawler_factory import CrawlerFactory


class PixivisionService:
    def __init__(self, proxy_config=None):
        """
        初始化 Pixivision 服务
        :param proxy_config: 代理配置
        """
        self.base_url = "https://www.pixivision.net/zh/c/illustration"
        self.proxy_config = proxy_config
        self.crawler = CrawlerFactory.create_crawler("pixivision", [self.base_url], proxy_config)

    def get_illustration_list(self, start_page=1, end_page=1):
        """
        获取插画列表
        :param start_page: 开始页码
        :param end_page: 结束页码
        :return: 插画列表
        """
        return self.crawler.crawl_pages(self.base_url, start_page, end_page)

    def get_illustration_detail(self, illustration_url):
        """
        获取单个插画详情
        :param illustration_url: 插画详情页URL
        :return: 插画详情
        """
        # 创建一个临时爬虫实例来爬取详情页
        detail_crawler = CrawlerFactory.create_crawler("pixivision", [illustration_url], self.proxy_config)
        return detail_crawler.crawl()

    def save_illustrations(self, illustrations, storage=None):
        """
        存储插画数据
        :param illustrations: 插画列表
        :param storage: 存储对象，默认为None（仅返回数据）
        :return: 存储结果
        """
        if storage:
            # 这里可以实现具体的存储逻辑，例如保存到数据库或文件
            # 暂时仅返回数据
            pass
        return illustrations

    def get_illustration_by_id(self, illustration_id):
        """
        根据ID获取插画详情
        :param illustration_id: 插画ID
        :return: 插画详情
        """
        illustration_url = f"https://www.pixivision.net/zh/a/{illustration_id}"
        return self.get_illustration_detail(illustration_url)
