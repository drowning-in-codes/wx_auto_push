from bs4 import BeautifulSoup

# 读取保存的 HTML 文件
with open("pixivision_list.html", "r", encoding="utf-8") as f:
    html = f.read()

# 解析 HTML
soup = BeautifulSoup(html, "lxml")

# 查找所有带 _article-card 类的元素
article_cards = soup.select("._article-card")
print(f"找到 {len(article_cards)} 个 _article-card 元素")

# 分析每个 _article-card 元素的结构
for i, card in enumerate(article_cards):
    print(f"\nCard {i+1}:")
    print(f"类: {card.get('class', [])}")
    print(f"完整结构:")
    print(card.prettify())
    print("-" * 80)
    
    # 查找链接
    links = card.find_all("a")
    print(f"链接数量: {len(links)}")
    for j, link in enumerate(links):
        print(f"链接 {j+1}: {link.get('href')}")
        print(f"链接文本: {link.text.strip()}")
    
    # 查找标题
    titles = card.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    print(f"标题数量: {len(titles)}")
    for j, title in enumerate(titles):
        print(f"标题 {j+1}: {title.text.strip()}")
    
    # 查找图片
    imgs = card.find_all("img")
    print(f"图片数量: {len(imgs)}")
    for j, img in enumerate(imgs):
        print(f"图片 {j+1}: {img.get('src')}")
    
    # 查找标签
    tags = card.find_all(class_=["tag", "tags", "tag-item"])
    print(f"标签数量: {len(tags)}")
    for j, tag in enumerate(tags):
        print(f"标签 {j+1}: {tag.text.strip()}")
    
    print("=" * 80)
