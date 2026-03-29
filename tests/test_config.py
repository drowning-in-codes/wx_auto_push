import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.utils.config import Config


class TestConfig(unittest.TestCase):
    """Config模块测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_config = {
            "wechat": {
                "app_id": "test_app_id",
                "app_secret": "test_app_secret",
                "template_id": "test_template_id",
            },
            "proxy": {
                "enabled": False,
                "http_proxy": "http://127.0.0.1:7890",
                "https_proxy": "http://127.0.0.1:7890",
            },
            "request": {"delay": 1},
            "download": {
                "max_workers": 5,
                "max_retries": 3,
                "directory": "./downloads",
            },
            "schedule": {
                "weekly_frequency": 3,
                "time_range": {"start": "08:00", "end": "20:00"},
                "upload": {
                    "start_page": 2,
                    "end_page": 5,
                    "title": "测试标题",
                    "author": "测试作者",
                    "compress": False,
                    "digest": "测试摘要",
                    "content": "测试内容",
                    "show_cover": 0,
                    "message_type": "news",
                },
            },
            "image_compression": {
                "enabled": True,
                "max_size": 1048576,
                "max_dimension": 2000,
                "quality": 85,
            },
            "draft": {"default_author": "test_author", "default_show_cover": 1},
        }

    def setUp(self):
        """测试前准备"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def _create_config_with_mock(self):
        """创建带有mock的Config实例"""
        with patch("src.utils.config.load_dotenv"):
            with patch.dict(os.environ, {}, clear=True):
                config = Config(self.temp_file.name)
                config.config = self.test_config.copy()
                return config

    def test_get_wechat_config(self):
        """测试获取微信配置"""
        config = self._create_config_with_mock()
        wechat_config = config.get_wechat_config()
        self.assertEqual(wechat_config.get("app_id"), "test_app_id")
        self.assertEqual(wechat_config.get("app_secret"), "test_app_secret")
        self.assertEqual(wechat_config.get("template_id"), "test_template_id")

    def test_get_proxy_config(self):
        """测试获取代理配置"""
        config = self._create_config_with_mock()
        proxy_config = config.get_proxy_config()
        self.assertEqual(proxy_config.get("enabled"), False)
        self.assertEqual(proxy_config.get("http_proxy"), "http://127.0.0.1:7890")
        self.assertEqual(proxy_config.get("https_proxy"), "http://127.0.0.1:7890")

    def test_get_request_config(self):
        """测试获取请求配置"""
        config = self._create_config_with_mock()
        request_config = config.get_request_config()
        self.assertEqual(request_config.get("delay"), 1)

    def test_get_download_config(self):
        """测试获取下载配置"""
        config = self._create_config_with_mock()
        download_config = config.get_download_config()
        self.assertEqual(download_config.get("max_workers"), 5)
        self.assertEqual(download_config.get("max_retries"), 3)
        self.assertEqual(download_config.get("directory"), "./downloads")

    def test_get_download_directory(self):
        """测试获取下载目录"""
        config = self._create_config_with_mock()
        download_dir = config.get_download_directory()
        self.assertEqual(download_dir, "./downloads")

    def test_get_schedule_config(self):
        """测试获取调度配置"""
        config = self._create_config_with_mock()
        schedule_config = config.get_schedule_config()
        self.assertEqual(schedule_config.get("weekly_frequency"), 3)
        time_range = schedule_config.get("time_range", {})
        self.assertEqual(time_range.get("start"), "08:00")
        self.assertEqual(time_range.get("end"), "20:00")

    def test_get_image_compression_config(self):
        """测试获取图片压缩配置"""
        config = self._create_config_with_mock()
        compression_config = config.get_image_compression_config()
        self.assertEqual(compression_config.get("enabled"), True)
        self.assertEqual(compression_config.get("max_size"), 1048576)
        self.assertEqual(compression_config.get("max_dimension"), 2000)
        self.assertEqual(compression_config.get("quality"), 85)

    def test_get_draft_config(self):
        """测试获取草稿配置"""
        config = self._create_config_with_mock()
        draft_config = config.get_draft_config()
        self.assertEqual(draft_config.get("default_author"), "test_author")
        self.assertEqual(draft_config.get("default_show_cover"), 1)

    def test_get_upload_config(self):
        """测试获取上传配置"""
        config = self._create_config_with_mock()
        upload_config = config.get_upload_config()
        self.assertEqual(upload_config.get("start_page"), 2)
        self.assertEqual(upload_config.get("end_page"), 5)
        self.assertEqual(upload_config.get("title"), "测试标题")
        self.assertEqual(upload_config.get("author"), "测试作者")
        self.assertEqual(upload_config.get("compress"), False)
        self.assertEqual(upload_config.get("digest"), "测试摘要")
        self.assertEqual(upload_config.get("content"), "测试内容")
        self.assertEqual(upload_config.get("show_cover"), 0)
        self.assertEqual(upload_config.get("message_type"), "news")

    def test_get_upload_config_default(self):
        """测试获取上传配置（默认值）"""
        config = self._create_config_with_mock()
        # 移除upload配置
        del config.config["schedule"]["upload"]
        upload_config = config.get_upload_config()
        # 验证默认值
        self.assertEqual(upload_config.get("start_page"), 1)
        self.assertEqual(upload_config.get("end_page"), 3)
        self.assertEqual(upload_config.get("title"), "")
        self.assertEqual(upload_config.get("author"), "")
        self.assertEqual(upload_config.get("compress"), True)
        self.assertEqual(upload_config.get("digest"), "")
        self.assertEqual(upload_config.get("content"), "")
        self.assertEqual(upload_config.get("show_cover"), 1)
        self.assertEqual(upload_config.get("message_type"), "newspic")

    def test_get_with_default(self):
        """测试获取不存在的配置项返回默认值"""
        config = self._create_config_with_mock()
        result = config.get("non_existent_key", "default_value")
        self.assertEqual(result, "default_value")

    def test_config_file_not_exists(self):
        """测试配置文件不存在时使用默认配置"""
        with patch("src.utils.config.load_dotenv"):
            config = Config("non_existent_config.json")
            self.assertIsNotNone(config.config)


if __name__ == "__main__":
    unittest.main()
