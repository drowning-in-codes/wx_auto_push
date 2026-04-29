import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.utils.proxy_pool_service import ProxyPoolService


class TestProxyPoolService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file_path = os.path.join(self.temp_dir, "proxy_pool_cache.json")
        self.proxy_pool_config = {
            "enabled": True,
            "api_url": "https://proxy.scdn.io/api/get_proxy.php",
            "protocol": "all",
            "count": 1,
            "country_code": "all",
            "fetch_interval": 60,
            "max_proxies": 10,
            "cache_file_path": self.cache_file_path,
            "proxy_config": {
                "enabled": False,
                "http_proxy": "http://localhost:7890",
                "https_proxy": "http://localhost:7890",
            },
        }

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _write_cache(self, proxies, last_fetch_time=1234567890):
        with open(self.cache_file_path, "w", encoding="utf-8") as cache_file:
            json.dump(
                {
                    "last_fetch_time": last_fetch_time,
                    "proxies": proxies,
                },
                cache_file,
                ensure_ascii=False,
                indent=2,
            )

    def test_load_cached_proxies_on_init(self):
        self._write_cache(["127.0.0.1:8080", "127.0.0.1:8081"])

        service = ProxyPoolService(self.proxy_pool_config)

        self.assertEqual(service.proxies, ["127.0.0.1:8080", "127.0.0.1:8081"])
        self.assertEqual(service.last_fetch_time, 1234567890)

    def test_fetch_proxies_saves_cache(self):
        service = ProxyPoolService(self.proxy_pool_config)

        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "data": {"proxies": ["10.0.0.1:9000", "10.0.0.2:9000"]}
        }

        session = MagicMock()
        session.get.return_value = response

        with patch(
            "src.utils.proxy_pool_service.requests.Session", return_value=session
        ):
            proxies = service.fetch_proxies()

        self.assertEqual(proxies, ["10.0.0.1:9000", "10.0.0.2:9000"])
        self.assertTrue(os.path.exists(self.cache_file_path))

        with open(self.cache_file_path, "r", encoding="utf-8") as cache_file:
            cache_data = json.load(cache_file)

        self.assertEqual(cache_data["proxies"], ["10.0.0.1:9000", "10.0.0.2:9000"])
        self.assertGreater(cache_data["last_fetch_time"], 0)

    def test_fetch_proxies_failure_keeps_existing_cache(self):
        self._write_cache(["127.0.0.1:8080"])
        service = ProxyPoolService(self.proxy_pool_config)

        session = MagicMock()
        session.get.side_effect = Exception("network error")

        with patch(
            "src.utils.proxy_pool_service.requests.Session", return_value=session
        ):
            proxies = service.fetch_proxies()

        self.assertEqual(service.proxies, ["127.0.0.1:8080"])
        self.assertEqual(proxies, ["127.0.0.1:8080"])

        with open(self.cache_file_path, "r", encoding="utf-8") as cache_file:
            cache_data = json.load(cache_file)

        self.assertEqual(cache_data["proxies"], ["127.0.0.1:8080"])

    def test_get_proxy_refreshes_when_cached_proxy_is_invalid(self):
        self._write_cache(["127.0.0.1:8080"])
        service = ProxyPoolService(self.proxy_pool_config)

        def refresh_proxy_pool():
            service.proxies = ["10.0.0.1:9000"]
            service.last_fetch_time = 1234567891

        with patch.object(service, "_is_proxy_available", side_effect=[False, True]):
            with patch.object(
                service, "fetch_proxies", side_effect=refresh_proxy_pool
            ) as mock_fetch:
                proxy = service.get_proxy()

        self.assertEqual(
            proxy,
            {"http": "http://10.0.0.1:9000", "https": "http://10.0.0.1:9000"},
        )
        mock_fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
