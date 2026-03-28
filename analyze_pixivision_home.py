import requests
from bs4 import BeautifulSoup

url = "https://www.pixivision.net/zh/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 禁用系统代理
session = requests.Session()
session.trust_env = False

response = session.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

# 查找 sidebar-contents-container
sidebar = soup.select_one(".sidebar-contents-container")
if sidebar:
    print("Sidebar 内容:")
    print(sidebar.prettify())
else:
    print("未找到 sidebar-contents-container")
