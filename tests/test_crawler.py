import unittest
from unittest.mock import Mock, patch, MagicMock
from src.crawlers.base_crawler import BaseCrawler
from src.crawlers.crawler_factory import CrawlerFactory


class TestBaseCrawler(unittest.TestCase):
    """BaseCrawler模块测试"""

    def setUp(self):
        """测试前准备"""
        self.urls = ["https://example.com"]
        self.proxy_config = {
            "enabled": False,
            "http_proxy": "http://127.0.0.1:7890",
            "https_proxy": "http://127.0.0.1:7890",
        }

    def test_init(self):
        """测试初始化"""
        crawler = BaseCrawler(self.urls, self.proxy_config)
        self.assertEqual(crawler.urls, self.urls)
        self.assertEqual(crawler.proxy_config, self.proxy_config)

    def test_init_without_proxy(self):
        """测试不带代理初始化"""
        crawler = BaseCrawler(self.urls)
        self.assertEqual(crawler.proxy_config, {})

    def test_get_random_url(self):
        """测试获取随机URL"""
        crawler = BaseCrawler(self.urls)
        url = crawler.get_random_url()
        self.assertIn(url, self.urls)

    def test_get_proxies_disabled(self):
        """测试代理禁用时获取代理配置"""
        crawler = BaseCrawler(self.urls, self.proxy_config)
        proxies = crawler._get_proxies()
        self.assertIsNone(proxies)

    def test_get_proxies_enabled(self):
        """测试代理启用时获取代理配置"""
        proxy_config = {
            "enabled": True,
            "http_proxy": "http://127.0.0.1:7890",
            "https_proxy": "http://127.0.0.1:7890",
        }
        crawler = BaseCrawler(self.urls, proxy_config)
        proxies = crawler._get_proxies()
        self.assertEqual(proxies["http"], "http://127.0.0.1:7890")
        self.assertEqual(proxies["https"], "http://127.0.0.1:7890")

    def test_get_headers(self):
        """测试获取请求头"""
        crawler = BaseCrawler(self.urls)
        headers = crawler._get_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Mozilla", headers["User-Agent"])

    @patch("requests.get")
    def test_crawl_success(self, mock_get):
        """测试爬取成功"""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        class TestCrawler(BaseCrawler):
            def parse(self, html, url):
                return {"title": "Test"}

        crawler = TestCrawler(self.urls)
        result = crawler.crawl()
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Test")

    def test_parse_not_implemented(self):
        """测试parse方法未实现"""
        crawler = BaseCrawler(self.urls)
        with self.assertRaises(NotImplementedError):
            crawler.parse("<html></html>", "https://example.com")


class TestCrawlerFactory(unittest.TestCase):
    """爬虫工厂测试"""

    def test_create_pixivision_crawler(self):
        """测试创建Pixivision爬虫"""
        from src.crawlers.pixivision_crawler import PixivisionCrawler

        crawler = CrawlerFactory.create_crawler(
            "pixivision", ["https://www.pixivision.net/zh/c/illustration"]
        )
        self.assertIsInstance(crawler, PixivisionCrawler)

    def test_create_anime_crawler(self):
        """测试创建动漫爬虫"""
        from src.crawlers.anime_crawler import AnimeCrawler

        crawler = CrawlerFactory.create_crawler("anime", ["https://example.com/anime"])
        self.assertIsInstance(crawler, AnimeCrawler)

    def test_create_image_crawler(self):
        """测试创建图片爬虫"""
        from src.crawlers.image_crawler import ImageCrawler

        crawler = CrawlerFactory.create_crawler("image", ["https://example.com/image"])
        self.assertIsInstance(crawler, ImageCrawler)

    def test_create_invalid_crawler(self):
        """测试创建无效爬虫类型"""
        with self.assertRaises(ValueError):
            CrawlerFactory.create_crawler("invalid", ["https://example.com"])


class TestPixivisionCrawler(unittest.TestCase):
    """Pixivision爬虫测试"""

    def setUp(self):
        """测试前准备"""
        self.urls = ["https://www.pixivision.net/zh/c/illustration"]
        self.proxy_config = {"enabled": False}

    @patch("requests.get")
    def test_crawl_one(self, mock_get):
        """测试爬取单个页面"""
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <div class="article-card">
                    <a href="/zh/a/12345">Test Article</a>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        from src.crawlers.pixivision_crawler import PixivisionCrawler

        crawler = PixivisionCrawler(self.urls, self.proxy_config)

        result = crawler.crawl()
        self.assertIsNotNone(result)

    def test_parse_illustration_id(self):
        """测试解析插画ID"""
        from src.crawlers.pixivision_crawler import PixivisionCrawler

        crawler = PixivisionCrawler(self.urls)

        url = "https://www.pixivision.net/zh/a/12345"
        import re

        match = re.search(r"/a/(\d+)", url)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "12345")


if __name__ == "__main__":
    unittest.main()
