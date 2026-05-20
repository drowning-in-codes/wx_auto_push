import os
import unittest
import curl_cffi
from curl_cffi import requests
class TestDownloadListIntegration(unittest.TestCase):
    """集成测试：访问 Pixivision 插画列表页面。

    默认跳过，运行前请设置环境变量 `RUN_PIXIVISION_INTEGRATION=1`。
    若需要登录态，可设置环境变量 `PIXIV_COOKIE` 为浏览器复制的 cookie 字符串。
    """

    @unittest.skipUnless(
        os.environ.get("RUN_PIXIVISION_INTEGRATION") == "1",
        "integration test: set RUN_PIXIVISION_INTEGRATION=1 to run",
    )
    def test_access_pixivision_illustration_list(self):
        url = "https://www.pixivision.net/zh/c/illustration"
        params = {"p": 1}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.pixivision.net/",
        }

        cookie = os.environ.get("PIXIV_COOKIE")
        if cookie:
            headers["Cookie"] = cookie

        resp = requests.get(url, params=params, headers=headers, timeout=30)
        # 如果服务器返回403或其他错误，raise_for_status 会抛异常，测试失败
        resp.raise_for_status()
        print(resp)
        self.assertEqual(resp.status_code, 200)
        # 页面应包含 Pixivision 的关键类或文字，至少包含站点名
        self.assertIn("pixivision", resp.text.lower())


if __name__ == "__main__":
    # unittest.main()
    url = "https://www.pixivision.net/zh/c/illustration"
    params = {"p": 1}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
    }

    resp = requests.get(url, params=params, headers=headers, timeout=30)
    # 如果服务器返回403或其他错误，raise_for_status 会抛异常，测试失败
    resp.raise_for_status()
    print(resp.text)
