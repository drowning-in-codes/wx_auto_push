import pytest
from unittest.mock import MagicMock, patch
from src.push.pixivision_service import PixivisionService


class TestPixivisionService:
    """测试 Pixivision 服务"""

    @pytest.fixture
    def pixivision_service(self):
        """创建 Pixivision 服务实例"""
        return PixivisionService()

    def test_get_illustration_list(self, pixivision_service):
        """测试获取插画列表"""
        # 模拟爬虫的 crawl_pages 方法
        with patch.object(pixivision_service.crawler, 'crawl_pages') as mock_crawl_pages:
            # 设置模拟返回值
            expected_result = [
                {
                    "title": "测试插画1",
                    "url": "https://www.pixivision.net/zh/a/12345",
                    "image_url": "https://example.com/image1.jpg",
                    "tags": ["插画", "测试"],
                    "source": "Pixivision"
                },
                {
                    "title": "测试插画2",
                    "url": "https://www.pixivision.net/zh/a/67890",
                    "image_url": "https://example.com/image2.jpg",
                    "tags": ["插画", "测试"],
                    "source": "Pixivision"
                }
            ]
            mock_crawl_pages.return_value = expected_result

            # 执行测试
            result = pixivision_service.get_illustration_list(1, 2)

            # 验证结果
            assert result == expected_result
            mock_crawl_pages.assert_called_once_with(
                "https://www.pixivision.net/zh/c/illustration", 1, 2
            )

    def test_get_illustration_detail(self, pixivision_service):
        """测试获取插画详情"""
        # 模拟爬虫的 crawl 方法
        with patch('src.crawlers.crawler_factory.CrawlerFactory.create_crawler') as mock_create_crawler:
            # 创建模拟的爬虫实例
            mock_crawler = MagicMock()
            mock_create_crawler.return_value = mock_crawler
            
            # 设置模拟返回值
            expected_result = {
                "title": "测试插画详情",
                "url": "https://www.pixivision.net/zh/a/12345",
                "content": "这是测试插画的介绍文字",
                "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
                "tags": ["插画", "测试"],
                "source": "Pixivision"
            }
            mock_crawler.crawl.return_value = expected_result

            # 执行测试
            illustration_url = "https://www.pixivision.net/zh/a/12345"
            result = pixivision_service.get_illustration_detail(illustration_url)

            # 验证结果
            assert result == expected_result
            mock_create_crawler.assert_called_once_with(
                "pixivision", [illustration_url], None
            )
            mock_crawler.crawl.assert_called_once()

    def test_get_illustration_by_id(self, pixivision_service):
        """测试根据ID获取插画详情"""
        # 模拟 get_illustration_detail 方法
        with patch.object(pixivision_service, 'get_illustration_detail') as mock_get_detail:
            # 设置模拟返回值
            expected_result = {
                "title": "测试插画详情",
                "url": "https://www.pixivision.net/zh/a/11525",
                "content": "这是测试插画的介绍文字",
                "images": ["https://example.com/image1.jpg"],
                "tags": ["插画", "测试"],
                "source": "Pixivision"
            }
            mock_get_detail.return_value = expected_result

            # 执行测试
            illustration_id = "11525"
            result = pixivision_service.get_illustration_by_id(illustration_id)

            # 验证结果
            assert result == expected_result
            mock_get_detail.assert_called_once_with(
                "https://www.pixivision.net/zh/a/11525"
            )

    def test_save_illustrations(self, pixivision_service):
        """测试存储插画数据"""
        # 测试数据
        illustrations = [
            {
                "title": "测试插画1",
                "url": "https://www.pixivision.net/zh/a/12345",
                "image_url": "https://example.com/image1.jpg",
                "tags": ["插画", "测试"],
                "source": "Pixivision"
            }
        ]

        # 执行测试
        result = pixivision_service.save_illustrations(illustrations)

        # 验证结果
        assert result == illustrations
