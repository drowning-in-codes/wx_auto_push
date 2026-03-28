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

# 查找 sidebar-container
sidebar = soup.select_one(".sidebar-container")
if sidebar:
    print("Sidebar 结构:")
    # 查找所有 sidebar-contents-container
    contents_containers = sidebar.select(".sidebar-contents-container")
    print(f"找到 {len(contents_containers)} 个 sidebar-contents-container")
    print()
    
    for i, container in enumerate(contents_containers, 1):
        print(f"第 {i} 个 sidebar-contents-container:")
        print(container.prettify())
        print("=" * 50)
else:
    print("未找到 sidebar-container")
