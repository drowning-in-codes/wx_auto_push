import unittest
import os
import json
import tempfile
from src.utils.config import Config


class TestConfig(unittest.TestCase):
    """Config模块测试"""

    def setUp(self):
        """测试前准备"""
        self.test_config = {
            "wechat": {
                "app_id": "test_app_id",
                "app_secret": "test_app_secret",
                "template_id": "test_template_id"
            },
            "proxy": {
                "enabled": False,
                "http_proxy": "http://127.0.0.1:7890",
                "https_proxy": "http://127.0.0.1:7890"
            },
            "request": {
                "delay": 1
            },
            "download": {
                "max_workers": 5,
                "max_retries": 3,
                "directory": "./downloads"
            },
            "schedule": {
                "weekly_frequency": 3,
                "time_range": {
                    "start": "08:00",
                    "end": "20:00"
                }
            },
            "image_compression": {
                "enabled": True,
                "max_size": 1048576,
                "max_dimension": 2000,
                "quality": 85
            },
            "draft": {
                "default_author": "test_author",
                "default_show_cover": 1
            }
        }
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()
        self.config = Config(self.temp_file.name)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_get_wechat_config(self):
        """测试获取微信配置"""
        wechat_config = self.config.get_wechat_config()
        self.assertEqual(wechat_config["app_id"], "test_app_id")
        self.assertEqual(wechat_config["app_secret"], "test_app_secret")
        self.assertEqual(wechat_config["template_id"], "test_template_id")

    def test_get_proxy_config(self):
        """测试获取代理配置"""
        proxy_config = self.config.get_proxy_config()
        self.assertEqual(proxy_config["enabled"], False)
        self.assertEqual(proxy_config["http_proxy"], "http://127.0.0.1:7890")
        self.assertEqual(proxy_config["https_proxy"], "http://127.0.0.1:7890")

    def test_get_request_config(self):
        """测试获取请求配置"""
        request_config = self.config.get_request_config()
        self.assertEqual(request_config["delay"], 1)

    def test_get_download_config(self):
        """测试获取下载配置"""
        download_config = self.config.get_download_config()
        self.assertEqual(download_config["max_workers"], 5)
        self.assertEqual(download_config["max_retries"], 3)
        self.assertEqual(download_config["directory"], "./downloads")

    def test_get_download_directory(self):
        """测试获取下载目录"""
        download_dir = self.config.get_download_directory()
        self.assertEqual(download_dir, "./downloads")

    def test_get_schedule_config(self):
        """测试获取调度配置"""
        schedule_config = self.config.get_schedule_config()
        self.assertEqual(schedule_config["weekly_frequency"], 3)
        self.assertEqual(schedule_config["time_range"]["start"], "08:00")
        self.assertEqual(schedule_config["time_range"]["end"], "20:00")

    def test_get_image_compression_config(self):
        """测试获取图片压缩配置"""
        compression_config = self.config.get_image_compression_config()
        self.assertEqual(compression_config["enabled"], True)
        self.assertEqual(compression_config["max_size"], 1048576)
        self.assertEqual(compression_config["max_dimension"], 2000)
        self.assertEqual(compression_config["quality"], 85)

    def test_get_draft_config(self):
        """测试获取草稿配置"""
        draft_config = self.config.get_draft_config()
        self.assertEqual(draft_config["default_author"], "test_author")
        self.assertEqual(draft_config["default_show_cover"], 1)

    def test_get_with_default(self):
        """测试获取不存在的配置项返回默认值"""
        result = self.config.get("non_existent_key", "default_value")
        self.assertEqual(result, "default_value")

    def test_config_file_not_exists(self):
        """测试配置文件不存在时使用默认配置"""
        config = Config("non_existent_config.json")
        self.assertIsNotNone(config.config)


if __name__ == '__main__':
    unittest.main()
