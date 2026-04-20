import requests
import logging
import time
import random

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

    def fetch_proxies(self):
        """
        从API获取代理
        :return: 代理列表
        """
        try:
            params = {
                "protocol": self.config.get("protocol", "all"),
                "count": self.config.get("count", 5),
                "country_code": self.config.get("country_code", ""),
            }

            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            # 解析新的返回格式
            proxies = data.get("data", {}).get("proxies", [])

            if proxies:
                self.proxies = proxies[: self.max_proxies]
                self.last_fetch_time = time.time()
                logger.info(f"成功获取 {len(self.proxies)} 个代理")
            else:
                logger.warning("未获取到代理")

        except Exception as e:
            logger.error(f"获取代理失败: {e}")

    def get_proxy(self):
        """
        获取一个代理
        :return: 代理字典 {"http": "...", "https": "..."}
        """
        # 检查是否需要刷新代理
        if not self.proxies or time.time() - self.last_fetch_time > self.fetch_interval:
            self.fetch_proxies()

        if not self.proxies:
            return None

        # 随机选择一个代理
        proxy = random.choice(self.proxies)
        proxy_url = f"http://{proxy}"

        return {"http": proxy_url, "https": proxy_url}

    def get_proxies(self):
        """
        获取所有代理
        :return: 代理列表
        """
        if not self.proxies or time.time() - self.last_fetch_time > self.fetch_interval:
            self.fetch_proxies()

        return self.proxies
