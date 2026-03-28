from bs4 import BeautifulSoup

# 读取保存的 HTML 文件
with open("pixivision_detail.html", "r", encoding="utf-8") as f:
    html = f.read()

# 解析 HTML
soup = BeautifulSoup(html, "lxml")

# 查找 article-item _feature-article-body__paragraph 元素
print("查找 article-item _feature-article-body__paragraph 元素:")
content_elements = soup.select(".article-item._feature-article-body__paragraph")
print(f"找到 {len(content_elements)} 个元素")

# 分析每个元素的结构
for i, element in enumerate(content_elements):
    print(f"\n元素 {i+1}:")
    print(element.prettify())
    print(f"  文本内容: {element.text.strip()[:200]}...")

# 查找其他可能的内容元素
print("\n查找其他可能的内容元素:")
other_elements = soup.select(".article-body, .feature-article-body, .article-content")
for i, element in enumerate(other_elements):
    print(f"\n元素 {i+1}:")
    print(f"  类: {element.get('class', [])}")
    print(f"  文本内容: {element.text.strip()[:200]}...")
