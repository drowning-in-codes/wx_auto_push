import json
import logging
import os
import random
import time

import requests

logger = logging.getLogger(__name__)


class ProxyPoolService:
    def __init__(self, proxy_pool_config=None):
        """
        初始化代理池服务
        :param proxy_pool_config: 代理池配置
        """
        self.config = proxy_pool_config or {}
        self.api_url = self.config.get(
            "api_url", "https://proxy.scdn.io/api/get_proxy.php"
        )
        self.proxies = []
        self.last_fetch_time = 0
        self.fetch_interval = self.config.get("fetch_interval", 60)  # 默认60秒
        self.max_proxies = self.config.get("max_proxies", 10)  # 默认最多10个代理
        self.cache_file_path = self.config.get(
            "cache_file_path", "data/proxy_pool_cache.json"
        )

        self._ensure_cache_directory()
        self._load_cached_proxies()

    def _ensure_cache_directory(self):
        """确保缓存文件目录存在"""
        cache_directory = os.path.dirname(os.path.abspath(self.cache_file_path))
        if cache_directory and not os.path.exists(cache_directory):
            os.makedirs(cache_directory, exist_ok=True)

    def _load_cached_proxies(self):
        """从本地缓存文件加载代理"""
        try:
            if not os.path.exists(self.cache_file_path):
                return False

            with open(self.cache_file_path, "r", encoding="utf-8") as cache_file:
                cache_data = json.load(cache_file)

            if isinstance(cache_data, dict):
                proxies = cache_data.get("proxies", [])
                last_fetch_time = cache_data.get("last_fetch_time", 0)
            elif isinstance(cache_data, list):
                proxies = cache_data
                last_fetch_time = os.path.getmtime(self.cache_file_path)
            else:
                return False

            if proxies:
                self.proxies = proxies[: self.max_proxies]
                self.last_fetch_time = float(last_fetch_time) if last_fetch_time else 0
                logger.info(f"从本地缓存加载 {len(self.proxies)} 个代理")
                return True

            return False
        except Exception as e:
            logger.warning(f"加载代理缓存失败: {e}")
            return False

    def _save_cached_proxies(self):
        """保存代理到本地缓存文件"""
        try:
            cache_data = {
                "last_fetch_time": self.last_fetch_time,
                "proxies": self.proxies[: self.max_proxies],
            }
            with open(self.cache_file_path, "w", encoding="utf-8") as cache_file:
                json.dump(cache_data, cache_file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.warning(f"保存代理缓存失败: {e}")
            return False

    def _get_available_proxy_from_pool(self):
        """从当前代理池中获取一个可用代理"""
        for _ in range(len(self.proxies)):
            proxy = random.choice(self.proxies)
            proxy_url = f"http://{proxy}"

            if self._is_proxy_available(proxy_url):
                return {"http": proxy_url, "https": proxy_url}

            logger.warning(f"代理 {proxy} 不可用，尝试下一个")
            self.proxies.remove(proxy)

        return None

    def fetch_proxies(self):
        """
        从API获取代理
        :return: 代理列表
        """
        try:
            protocol = self.config.get("protocol", "all")
            count = self.config.get("count", 5)
            country_code = self.config.get("country_code", "all")

            # 检查空字符串，如果为空则使用默认值
            if not protocol or protocol.strip() == "":
                protocol = "all"
            if not count or str(count).strip() == "":
                count = 1
            if not country_code or country_code.strip() == "":
                country_code = "all"

            params = {
                "protocol": protocol,
                "count": count,
                "country_code": country_code,
            }

            # 创建会话，根据配置选择是否使用代理
            session = requests.Session()

            # 获取传统代理配置
            proxy_config = self.config.get("proxy_config", {})
            if proxy_config.get("enabled"):
                # 使用传统代理连接代理池API
                http_proxy = proxy_config.get("http_proxy", "")
                https_proxy = proxy_config.get("https_proxy", "")
                if http_proxy or https_proxy:
                    session.proxies = {
                        "http": http_proxy,
                        "https": https_proxy,
                    }
                    logger.info(f"使用传统代理连接代理池API: {http_proxy}")
            else:
                # 禁用系统代理，直接连接
                session.trust_env = False

            response = session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            # 解析新的返回格式
            proxies = data.get("data", {}).get("proxies", [])

            if proxies:
                self.proxies = proxies[: self.max_proxies]
                self.last_fetch_time = time.time()
                self._save_cached_proxies()
                logger.info(f"成功获取 {len(self.proxies)} 个代理")
                return self.proxies
            else:
                logger.warning("未获取到代理")
                return []

        except Exception as e:
            logger.error(f"获取代理失败: {e}")
            return self.proxies

    def get_proxy(self):
        """
        获取一个可用的代理
        :return: 代理字典 {"http": "...", "https": "..."}
        """
        # 优先使用本地缓存或当前内存中的代理
        if not self.proxies:
            self._load_cached_proxies()

        if self.proxies:
            proxy = self._get_available_proxy_from_pool()
            if proxy:
                return proxy

        # 当前代理池不可用时，再从API刷新
        if not self.proxies:
            self.fetch_proxies()

        if not self.proxies:
            return None

        proxy = self._get_available_proxy_from_pool()
        if proxy:
            return proxy

        # 所有代理都不可用时，回源刷新一次
        self.fetch_proxies()

        if not self.proxies:
            logger.warning("所有代理都不可用")
            return None

        proxy = self._get_available_proxy_from_pool()
        if proxy:
            return proxy

        logger.warning("所有代理都不可用")
        return None

    def _is_proxy_available(self, proxy_url):
        """
        检查代理是否可用
        :param proxy_url: 代理URL
        :return: 是否可用
        """
        try:
            # 创建会话，禁用系统代理，避免循环代理问题
            session = requests.Session()
            session.trust_env = False  # 禁用系统代理设置
            response = session.get(
                "http://www.google.com",
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_proxies(self):
        """
        获取所有代理
        :return: 代理列表
        """
        if not self.proxies:
            self._load_cached_proxies()

        if not self.proxies:
            self.fetch_proxies()

        return self.proxies
