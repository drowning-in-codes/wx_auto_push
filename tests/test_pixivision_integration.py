import os
import unittest

from src.crawlers.crawler_factory import CrawlerFactory


class TestPixivisionIntegration(unittest.TestCase):
    """Pixivision 集成测试（默认跳过，需设置环境变量 RUN_PIXIVISION_INTEGRATION=1 来运行）"""

    @unittest.skipUnless(
        os.environ.get("RUN_PIXIVISION_INTEGRATION") == "1",
        "integration test: set RUN_PIXIVISION_INTEGRATION=1 to run",
    )
    def test_crawl_pixivision_page_p1(self):
        """请求 https://www.pixivision.net/zh/c/illustration?p=1 并断言返回结构合理"""
        base_url = "https://www.pixivision.net/zh/c/illustration"
        crawler = CrawlerFactory.create_crawler("pixivision", [base_url])

        # 使用 crawl_pages 以确保请求 ?p=1
        results = crawler.crawl_pages(base_url, 1, 1)

        # 应返回列表（可能为空，但不应抛异常）
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)

        if results:
            first = results[0]
            self.assertIn("title", first)
            self.assertIn("url", first)
            self.assertIn("article_id", first)


if __name__ == "__main__":
    unittest.main()
