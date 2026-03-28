from bs4 import BeautifulSoup

# 读取保存的 HTML 文件
with open("pixivision_detail.html", "r", encoding="utf-8") as f:
    html = f.read()

# 解析 HTML
soup = BeautifulSoup(html, "lxml")

# 查找 div._article-illust-eyecatch 元素
print("查找 div._article-illust-eyecatch 元素:")
eyecatch_elements = soup.select("div._article-illust-eyecatch")
print(f"找到 {len(eyecatch_elements)} 个元素")

# 分析每个元素的结构
for i, element in enumerate(eyecatch_elements):
    print(f"\n元素 {i+1}:")
    print(element.prettify())
    
    # 查找其中的 img.aie__image 元素
    img = element.select_one("img.aie__image")
    if img:
        print(f"  图片 URL: {img.get('src')}")
