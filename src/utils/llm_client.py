import requests
import json


class LLMClient:
    def __init__(self, config, proxy_config=None):
        self.model = config.get("model", "openai")
        self.config = config
        self.proxy_config = proxy_config or {}

        if self.model == "openai":
            openai_config = config.get("openai", {})
            self.api_key = openai_config.get("api_key")
            self.api_url = openai_config.get("api_url")
            self.prompt = openai_config.get("prompt")
        elif self.model == "gemini":
            gemini_config = config.get("gemini", {})
            self.api_key = gemini_config.get("api_key")
            self.api_url = gemini_config.get("api_url")
            self.prompt = gemini_config.get("prompt")
        else:
            raise ValueError(f"不支持的模型类型: {self.model}")

    def _get_proxies(self):
        """
        获取代理配置
        """
        if self.proxy_config.get("enabled"):
            return {
                "http": self.proxy_config.get("http_proxy"),
                "https": self.proxy_config.get("https_proxy"),
            }
        return None

    def rewrite_content(self, content):
        if self.model == "openai":
            return self._rewrite_with_openai(content)
        elif self.model == "gemini":
            return self._rewrite_with_gemini(content)
        else:
            return content

    def generate_summary(self, content):
        if self.model == "openai":
            return self._summarize_with_openai(content)
        elif self.model == "gemini":
            return self._summarize_with_gemini(content)
        else:
            return content

    def _rewrite_with_openai(self, content):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": content},
                ],
                "max_tokens": 500,
            }

            response = requests.post(
                self.api_url, headers=headers, json=data, proxies=self._get_proxies()
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"调用OpenAI API失败: {e}")
            return content

    def _summarize_with_openai(self, content):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "请将以下内容总结为简短的微信公众号标题，不超过20字",
                    },
                    {"role": "user", "content": content},
                ],
                "max_tokens": 50,
            }

            response = requests.post(
                self.api_url, headers=headers, json=data, proxies=self._get_proxies()
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"调用OpenAI API失败: {e}")
            return content

    def _rewrite_with_gemini(self, content):
        try:
            headers = {"Content-Type": "application/json"}

            data = {
                "contents": [{"parts": [{"text": f"{self.prompt}\n\n{content}"}]}],
                "generationConfig": {"maxOutputTokens": 500},
            }

            url = f"{self.api_url}?key={self.api_key}"
            response = requests.post(
                url, headers=headers, json=data, proxies=self._get_proxies()
            )
            response.raise_for_status()

            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"调用Gemini API失败: {e}")
            return content

    def _summarize_with_gemini(self, content):
        try:
            headers = {"Content-Type": "application/json"}

            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"请将以下内容总结为简短的微信公众号标题，不超过20字\n\n{content}"
                            }
                        ]
                    }
                ],
                "generationConfig": {"maxOutputTokens": 50},
            }

            url = f"{self.api_url}?key={self.api_key}"
            response = requests.post(
                url, headers=headers, json=data, proxies=self._get_proxies()
            )
            response.raise_for_status()

            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"调用Gemini API失败: {e}")
            return content
