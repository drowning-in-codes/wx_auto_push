import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from src.push.pixivision_service import PixivisionService


class TestPixivisionService(unittest.TestCase):
    """Pixivision服务模块测试"""

    def setUp(self):
        """测试前准备"""
        self.proxy_config = {"enabled": False}
        self.request_config = {"delay": 1}
        self.temp_dir = tempfile.mkdtemp()
        self.storage_file = os.path.join(self.temp_dir, "test_illustrations.json")

        with patch("src.push.pixivision_service.CrawlerFactory.create_crawler"):
            self.service = PixivisionService(
                proxy_config=self.proxy_config,
                request_config=self.request_config,
                storage_type="json",
                file_path=self.storage_file,
            )

    def tearDown(self):
        """测试后清理"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.service.proxy_config, self.proxy_config)
        self.assertEqual(self.service.request_config, self.request_config)
        self.assertIsNotNone(self.service.storage)

    @patch("src.push.pixivision_service.CrawlerFactory.create_crawler")
    def test_get_illustration_list(self, mock_create_crawler):
        """测试获取插画列表"""
        mock_crawler = Mock()
        mock_crawler.crawl_pages.return_value = [
            {"article_id": "1", "title": "Test 1"},
            {"article_id": "2", "title": "Test 2"},
        ]
        mock_create_crawler.return_value = mock_crawler

        service = PixivisionService(
            proxy_config=self.proxy_config, request_config=self.request_config
        )

        illustrations = service.get_illustration_list(1, 1)
        self.assertEqual(len(illustrations), 2)

    @patch("src.push.pixivision_service.CrawlerFactory.create_crawler")
    def test_get_illustration_detail(self, mock_create_crawler):
        """测试获取插画详情"""
        mock_crawler = Mock()
        mock_crawler.crawl.return_value = {
            "article_id": "12345",
            "title": "Test Illustration",
            "images": ["https://example.com/image.jpg"],
        }
        mock_create_crawler.return_value = mock_crawler

        service = PixivisionService(
            proxy_config=self.proxy_config, request_config=self.request_config
        )

        illustration = service.get_illustration_detail(
            "https://www.pixivision.net/zh/a/12345"
        )
        self.assertIsNotNone(illustration)
        self.assertEqual(illustration["article_id"], "12345")

    def test_save_illustration(self):
        """测试保存插画"""
        illustration = {
            "article_id": "12345",
            "title": "Test Illustration",
            "url": "https://www.pixivision.net/zh/a/12345",
        }

        result = self.service.save_illustration(illustration)
        self.assertTrue(result)

        saved = self.service.storage.get_illustration("12345")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["title"], "Test Illustration")

    def test_get_illustration_by_id(self):
        """测试根据ID获取插画"""
        illustration = {"article_id": "12345", "title": "Test Illustration"}
        self.service.save_illustration(illustration)

        result = self.service.storage.get_illustration("12345")
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Test Illustration")

    def test_get_illustration_by_id_not_found(self):
        """测试获取不存在的插画"""
        result = self.service.storage.get_illustration("nonexistent")
        self.assertIsNone(result)

    def test_search_illustrations(self):
        """测试搜索插画"""
        illustrations = [
            {"article_id": "1", "title": "测试插画1", "tags": ["测试"]},
            {"article_id": "2", "title": "Test Illustration", "tags": ["test"]},
        ]
        for ill in illustrations:
            self.service.save_illustration(ill)

        results = self.service.search_illustrations("测试")
        self.assertGreaterEqual(len(results), 1)

    @patch("src.push.pixivision_service.requests.get")
    @patch("src.push.pixivision_service.CrawlerFactory.create_crawler")
    def test_download_illustration_images(self, mock_create_crawler, mock_get):
        """测试下载插画图片"""
        mock_crawler = Mock()
        mock_crawler.crawl.return_value = {
            "article_id": "12345",
            "title": "Test Illustration",
            "images": ["https://example.com/image1.jpg"],
        }
        mock_create_crawler.return_value = mock_crawler

        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        service = PixivisionService(
            proxy_config=self.proxy_config, request_config=self.request_config
        )

        download_dir = os.path.join(self.temp_dir, "downloads")
        success, path, files = service.download_illustration_images(
            "12345", download_dir, max_retries=1, max_workers=1
        )

        self.assertTrue(success)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(len(files), 1)

    def test_clean_title_for_folder_name(self):
        """测试清理标题作为文件夹名称"""
        title = "Test/Title:With*Invalid|Characters?"
        safe_title = "".join(
            c for c in title if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        self.assertNotIn("/", safe_title)
        self.assertNotIn(":", safe_title)
        self.assertNotIn("*", safe_title)
        self.assertNotIn("|", safe_title)
        self.assertNotIn("?", safe_title)


if __name__ == "__main__":
    unittest.main()
