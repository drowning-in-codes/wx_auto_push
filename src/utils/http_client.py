from __future__ import annotations

from copy import deepcopy
import mimetypes
import os

import curl_cffi
import requests as std_requests
from curl_cffi import requests as curl_requests

DEFAULT_HTTP_CLIENT_CONFIG = {
    "provider": "curl_cffi",
    "impersonate": "chrome124",
    "trust_env": False,
    "timeout": 60,
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
    # ensure timeout exists
    normalized["timeout"] = int(normalized.get("timeout", 60) or 0) or 60
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


class HttpClient:
    """统一的 HTTP 客户端封装。

    现在接收额外的 `proxy_config`（字典，形如 {"enabled": bool, "http_proxy":..., "https_proxy":...}），
    并在请求中作为默认代理使用；同时支持在配置中设置 `timeout` 默认值。
    """

    def __init__(self, config: dict | None = None, proxy_config: dict | None = None):
        self.config = normalize_http_client_config(config)
        self.session = create_session(self.config)
        self.proxy_config = proxy_config or {}
        self.default_timeout = int(self.config.get("timeout", 60) or 60)

    def request(self, method, url, **kwargs):
        """通过底层 session 发送请求。"""
        # fill default proxies and timeout if not provided
        if "proxies" not in kwargs:
            kwargs["proxies"] = self._build_proxies()
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.default_timeout
        return self.session.request(method, url, **kwargs)

    def _build_proxies(self):
        if self.proxy_config.get("enabled"):
            return {
                "http": self.proxy_config.get("http_proxy"),
                "https": self.proxy_config.get("https_proxy"),
            }
        return {"http": None, "https": None}

    def upload_img(
        self, url, media_file, data=None, headers=None, proxies=None, timeout=None
    ):
        """封装文件上传，其他请求继续直接使用 session.request。"""
        # decide proxies/timeout defaults
        if proxies is None:
            proxies = self._build_proxies()
        if timeout is None:
            timeout = self.default_timeout

        if self.config.get("provider") == "curl_cffi":
            multipart = curl_cffi.CurlMime()
            try:
                if isinstance(media_file, (str, bytes, os.PathLike)):
                    file_path = os.fspath(media_file)
                    file_name = os.path.basename(file_path)
                    content_type = (
                        mimetypes.guess_type(file_name)[0] or "application/octet-stream"
                    )
                    multipart.addpart(
                        name="media",
                        content_type=content_type,
                        filename=file_name,
                        local_path=file_path,
                    )
                else:
                    file_name = getattr(media_file, "name", None) or "media"
                    content_type = (
                        mimetypes.guess_type(file_name)[0] or "application/octet-stream"
                    )
                    media_file.seek(0)
                    multipart.addpart(
                        name="media",
                        content_type=content_type,
                        filename=os.path.basename(file_name),
                        data=media_file.read(),
                    )

                request_kwargs = {
                    "multipart": multipart,
                    "data": data or {},
                    "headers": headers or {},
                    "proxies": proxies,
                    "timeout": timeout,
                }
                request_kwargs = {
                    k: v for k, v in request_kwargs.items() if v is not None
                }
                return self.session.request("POST", url, **request_kwargs)
            finally:
                multipart.close()

        # requests-style upload: open file when a path is provided
        fileobj = None
        try:
            if isinstance(media_file, (str, bytes, os.PathLike)):
                file_path = os.fspath(media_file)
                fileobj = open(file_path, "rb")
                files = {"media": fileobj}
            else:
                files = {"media": media_file}

            request_kwargs = {
                "files": files,
                "data": data or {},
                "headers": headers or {},
                "proxies": proxies,
                "timeout": timeout,
            }
            request_kwargs = {k: v for k, v in request_kwargs.items() if v is not None}
            return self.session.request("POST", url, **request_kwargs)
        finally:
            if fileobj is not None:
                try:
                    fileobj.close()
                except Exception:
                    pass


def create_client(config: dict | None = None, proxy_config: dict | None = None):
    """创建统一 HTTP 客户端封装实例。

    支持传入 `proxy_config`，会传递给 `HttpClient` 保存为默认代理设置。
    """
    return HttpClient(config, proxy_config=proxy_config)
