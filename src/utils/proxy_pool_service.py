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
                logger.info(f"成功获取 {len(self.proxies)} 个代理")
            else:
                logger.warning("未获取到代理")

        except Exception as e:
            logger.error(f"获取代理失败: {e}")

    def get_proxy(self):
        """
        获取一个可用的代理
        :return: 代理字典 {"http": "...", "https": "..."}
        """
        # 检查是否需要刷新代理
        if not self.proxies or time.time() - self.last_fetch_time > self.fetch_interval:
            self.fetch_proxies()

        if not self.proxies:
            return None

        # 随机选择一个代理并检查可用性
        for _ in range(len(self.proxies)):
            proxy = random.choice(self.proxies)
            proxy_url = f"http://{proxy}"

            # 检查代理是否可用
            if self._is_proxy_available(proxy_url):
                return {"http": proxy_url, "https": proxy_url}
            else:
                logger.warning(f"代理 {proxy} 不可用，尝试下一个")
                # 从列表中移除不可用的代理
                self.proxies.remove(proxy)

        # 所有代理都不可用
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
        if not self.proxies or time.time() - self.last_fetch_time > self.fetch_interval:
            self.fetch_proxies()

        return self.proxies
