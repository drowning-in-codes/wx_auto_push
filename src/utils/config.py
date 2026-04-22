import json
import os
from dotenv import load_dotenv


class Config:
    def __init__(self, config_path="config.json"):
        # 加载环境变量
        load_dotenv()
        load_dotenv(".env.local")

        # 根据环境加载不同的配置文件
        env = os.getenv("NODE_ENV", "development")
        if env == "production":
            env_config_path = "config.production.json"
        else:
            env_config_path = "config.development.json"

        # 优先使用环境特定的配置文件
        if os.path.exists(env_config_path):
            self.config_path = env_config_path
        else:
            self.config_path = config_path

        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件，并从环境变量覆盖"""
        # 加载文件配置
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

        # 从环境变量覆盖配置
        self._override_from_env(config)

        return config

    def _override_from_env(self, config):
        """从环境变量覆盖配置"""
        # 微信配置
        if os.getenv("WECHAT_APP_ID"):
            if "wechat" not in config:
                config["wechat"] = {}
            config["wechat"]["app_id"] = os.getenv("WECHAT_APP_ID")
        if os.getenv("WECHAT_APP_SECRET"):
            if "wechat" not in config:
                config["wechat"] = {}
            config["wechat"]["app_secret"] = os.getenv("WECHAT_APP_SECRET")
        if os.getenv("WECHAT_TEMPLATE_ID"):
            if "wechat" not in config:
                config["wechat"] = {}
            config["wechat"]["template_id"] = os.getenv("WECHAT_TEMPLATE_ID")
        # 微信预览配置
        if os.getenv("WECHAT_PREVIEW_ENABLED"):
            if "wechat" not in config:
                config["wechat"] = {}
            if "preview" not in config["wechat"]:
                config["wechat"]["preview"] = {}
            config["wechat"]["preview"]["enabled"] = (
                os.getenv("WECHAT_PREVIEW_ENABLED").lower() == "true"
            )
        if os.getenv("WECHAT_PREVIEW_TOWXNAME"):
            if "wechat" not in config:
                config["wechat"] = {}
            if "preview" not in config["wechat"]:
                config["wechat"]["preview"] = {}
            config["wechat"]["preview"]["towxname"] = os.getenv(
                "WECHAT_PREVIEW_TOWXNAME"
            )

        # 微信回调配置
        if os.getenv("WECHAT_TOKEN"):
            if "wechat" not in config:
                config["wechat"] = {}
            config["wechat"]["token"] = os.getenv("WECHAT_TOKEN")
        if os.getenv("WECHAT_CALLBACK_ENABLED"):
            if "wechat" not in config:
                config["wechat"] = {}
            if "callback" not in config["wechat"]:
                config["wechat"]["callback"] = {}
            config["wechat"]["callback"]["enabled"] = (
                os.getenv("WECHAT_CALLBACK_ENABLED").lower() == "true"
            )
        if os.getenv("WECHAT_CALLBACK_HOST"):
            if "wechat" not in config:
                config["wechat"] = {}
            if "callback" not in config["wechat"]:
                config["wechat"]["callback"] = {}
            config["wechat"]["callback"]["host"] = os.getenv("WECHAT_CALLBACK_HOST")
        if os.getenv("WECHAT_CALLBACK_PORT"):
            if "wechat" not in config:
                config["wechat"] = {}
            if "callback" not in config["wechat"]:
                config["wechat"]["callback"] = {}
            config["wechat"]["callback"]["port"] = int(
                os.getenv("WECHAT_CALLBACK_PORT")
            )

        # 大模型配置
        if os.getenv("LLM_ENABLED"):
            if "llm" not in config:
                config["llm"] = {}
            config["llm"]["enabled"] = os.getenv("LLM_ENABLED").lower() == "true"
        if os.getenv("LLM_MODEL"):
            if "llm" not in config:
                config["llm"] = {}
            config["llm"]["model"] = os.getenv("LLM_MODEL")

        # OpenAI配置
        if os.getenv("OPENAI_API_KEY"):
            if "llm" not in config:
                config["llm"] = {}
            if "openai" not in config["llm"]:
                config["llm"]["openai"] = {}
            config["llm"]["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_API_URL"):
            if "llm" not in config:
                config["llm"] = {}
            if "openai" not in config["llm"]:
                config["llm"]["openai"] = {}
            config["llm"]["openai"]["api_url"] = os.getenv("OPENAI_API_URL")

        # Gemini配置
        if os.getenv("GEMINI_API_KEY"):
            if "llm" not in config:
                config["llm"] = {}
            if "gemini" not in config["llm"]:
                config["llm"]["gemini"] = {}
            config["llm"]["gemini"]["api_key"] = os.getenv("GEMINI_API_KEY")
        if os.getenv("GEMINI_API_URL"):
            if "llm" not in config:
                config["llm"] = {}
            if "gemini" not in config["llm"]:
                config["llm"]["gemini"] = {}
            config["llm"]["gemini"]["api_url"] = os.getenv("GEMINI_API_URL")

        # 调度配置
        if os.getenv("WEEKLY_FREQUENCY"):
            if "schedule" not in config:
                config["schedule"] = {}
            config["schedule"]["weekly_frequency"] = int(os.getenv("WEEKLY_FREQUENCY"))
        if os.getenv("TIME_RANGE_START") and os.getenv("TIME_RANGE_END"):
            if "schedule" not in config:
                config["schedule"] = {}
            config["schedule"]["time_range"] = {
                "start": os.getenv("TIME_RANGE_START"),
                "end": os.getenv("TIME_RANGE_END"),
            }

        # 代理配置
        proxy_enabled = False
        if os.getenv("PROXY_ENABLED"):
            if "proxy" not in config:
                config["proxy"] = {}
            proxy_enabled = os.getenv("PROXY_ENABLED").lower() == "true"
            config["proxy"]["enabled"] = proxy_enabled
        # 只有在启用代理时才加载代理地址
        if proxy_enabled:
            if os.getenv("HTTP_PROXY"):
                if "proxy" not in config:
                    config["proxy"] = {}
                config["proxy"]["http_proxy"] = os.getenv("HTTP_PROXY")
            if os.getenv("HTTPS_PROXY"):
                if "proxy" not in config:
                    config["proxy"] = {}
                config["proxy"]["https_proxy"] = os.getenv("HTTPS_PROXY")

        # 推送配置
        if os.getenv("IMAGE_PUBLISH_TYPE"):
            if "push" not in config:
                config["push"] = {}
            config["push"]["image_publish_type"] = os.getenv("IMAGE_PUBLISH_TYPE")

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_wechat_config(self):
        return self.get("wechat", {})

    def get_anime_sources(self):
        return self.get("data_sources.anime", [])

    def get_image_sources(self):
        return self.get("data_sources.images", [])

    def get_llm_config(self):
        return self.get("llm", {})

    def get_upload_config(self):
        return self.get(
            "schedule.upload",
            {
                "start_page": 1,
                "end_page": 3,
                "title": "",
                "author": "",
                "compress": True,
                "digest": "",
                "content": "",
                "show_cover": 1,
                "message_type": "newspic",
            },
        )

    def get_schedule_config(self):
        return self.get("schedule", {})

    def get_push_config(self):
        return self.get("push", {})

    def get_content_weights(self):
        """
        获取推送类型权重配置
        :return: 推送类型权重字典，例如 {"text": 1, "image": 1}
        """
        push_config = self.get("push", {})
        return push_config.get("content_weights", {"text": 1, "image": 1})

    def get_proxy_config(self):
        return self.get("proxy", {})

    def get_proxy_pool_config(self):
        """
        获取代理池配置
        :return: 代理池配置字典
        """
        return self.get(
            "proxy_pool",
            {
                "enabled": False,
                "api_url": "https://proxy.scdn.io/api/get_proxy.php",
                "protocol": "all",
                "count": 1,
                "country_code": "all",
                "fetch_interval": 60,
                "max_proxies": 10,
            },
        )

    def get_request_config(self):
        """
        获取请求配置
        :return: 请求配置字典
        """
        return self.get(
            "request",
            {
                "delay": 1,
            },
        )

    def get_download_config(self):
        """
        获取下载配置
        :return: 下载配置字典
        """
        return self.get(
            "download",
            {
                "max_workers": 5,
                "max_retries": 3,
                "directory": "./downloads",
                "enable_crawl_proxy_pool": True,
            },
        )

    def get_download_directory(self):
        """
        获取下载目录
        :return: 下载目录路径
        """
        download_config = self.get_download_config()
        return download_config.get("directory", "./downloads")

    def get_image_compression_config(self):
        """
        获取图片压缩配置
        :return: 图片压缩配置字典
        """
        return self.get(
            "image_compression",
            {
                "enabled": True,
                "max_size": 1048576,  # 1MB
                "max_dimension": 2000,
                "quality": 85,
            },
        )

    def get_draft_config(self):
        """
        获取草稿配置
        :return: 草稿配置字典
        """
        return self.get(
            "draft",
            {
                "default_author": "公众号作者",
                "default_material_type": "temporary",
                "default_show_cover": 1,
            },
        )

    def set(self, key, value):
        """
        设置配置值
        """
        keys = key.split(".")
        config = self.config

        # 导航到目标键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value

        # 保存配置到文件
        self._save_config()

    def _save_config(self):
        """
        保存配置到文件
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def set_push_time_range(self, start, end):
        """
        设置推送时间范围
        """
        self.set("schedule.time_range", {"start": start, "end": end})

    def set_weekly_push_frequency(self, frequency):
        """
        设置每周推送频率
        """
        self.set("schedule.weekly_frequency", frequency)
