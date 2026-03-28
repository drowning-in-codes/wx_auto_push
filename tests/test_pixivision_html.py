import requests
from bs4 import BeautifulSoup

# 获取 Pixivision 插画列表页面的 HTML
url = "https://www.pixivision.net/zh/c/illustration"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"请求成功，状态码: {response.status_code}")
    print(f"响应长度: {len(response.text)} 字符")

    # 保存 HTML 到文件
    with open("pixivision_list.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("HTML 已保存到 pixivision_list.html")

    # 解析 HTML 结构
    soup = BeautifulSoup(response.text, "lxml")

    # 查找所有 article 元素
    articles = soup.select("article")
    print(f"找到 {len(articles)} 个 article 元素")

    # 分析每个 article 元素的类和结构
    print("\n分析 article 元素:")
    for i, article in enumerate(articles):
        classes = article.get("class", [])
        print(f"Article {i+1} 类: {classes}")

        # 查找链接和标题
        link = article.select_one("a")
        title = article.select_one("h3, h4, .title")

        if link:
            print(f"  链接: {link.get('href')}")
        if title:
            print(f"  标题: {title.text.strip()}")

        # 查找图片
        img = article.select_one("img")
        if img:
            print(f"  图片: {img.get('src')}")

        # 查找标签
        tags = article.select(".tag, .tags, .tag-item")
        if tags:
            print(f"  标签: {[tag.text.strip() for tag in tags]}")

        print()

        # 只分析前 5 个元素，避免输出过多
        if i >= 4:
            print("... 省略其他元素 ...")
            break

    # 查找可能的卡片容器
    print("\n查找可能的卡片容器:")
    containers = soup.select("._article-list, .article-list, .list-container")
    for i, container in enumerate(containers):
        print(f"容器 {i+1} 类: {container.get('class', [])}")
        items = container.select("article")
        print(f"  包含 {len(items)} 个 article 元素")
        print()

except Exception as e:
    print(f"错误: {e}")
    import traceback

    traceback.print_exc()
