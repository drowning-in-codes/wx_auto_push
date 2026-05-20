from __future__ import annotations

from copy import deepcopy
import os

import requests as std_requests
from curl_cffi import requests as curl_requests

DEFAULT_HTTP_CLIENT_CONFIG = {
    "provider": "curl_cffi",
    "impersonate": "chrome124",
    "trust_env": False,
}


def normalize_http_client_config(config: dict | None = None) -> dict:
    """合并并规范化 HTTP 客户端配置。"""
    normalized = deepcopy(DEFAULT_HTTP_CLIENT_CONFIG)
    if config:
        normalized.update({k: v for k, v in config.items() if v is not None})

    provider = str(normalized.get("provider", "curl_cffi")).strip().lower()
    if provider in {"curl-cffi", "curl_cffi", "curlcffi", "curl"}:
        provider = "curl_cffi"
    elif provider in {"requests", "stdlib", "default"}:
        provider = "requests"
    else:
        provider = "curl_cffi"

    normalized["provider"] = provider
    normalized["trust_env"] = bool(normalized.get("trust_env", False))
    return normalized


def get_http_client_provider(config: dict | None = None) -> str:
    """返回当前 HTTP 客户端提供方名称。"""
    env_provider = os.getenv("HTTP_CLIENT_PROVIDER")
    if env_provider:
        return normalize_http_client_config({"provider": env_provider}).get(
            "provider", "curl_cffi"
        )
    return normalize_http_client_config(config).get("provider", "curl_cffi")


def get_requests_module(config: dict | None = None):
    """根据配置返回 requests 风格模块。"""
    provider = get_http_client_provider(config)
    return curl_requests if provider == "curl_cffi" else std_requests


def create_session(config: dict | None = None):
    """创建一个 requests/curl_cffi 兼容 Session。"""
    normalized = normalize_http_client_config(config)
    module = get_requests_module(normalized)

    session_kwargs = {}
    if normalized["provider"] == "curl_cffi" and normalized.get("impersonate"):
        session_kwargs["impersonate"] = normalized["impersonate"]

    session = module.Session(**session_kwargs)
    session.trust_env = normalized.get("trust_env", False)
    return session
