from bs4 import BeautifulSoup

# 读取保存的 HTML 文件
with open("pixivision_detail.html", "r", encoding="utf-8") as f:
    html = f.read()

# 解析 HTML
soup = BeautifulSoup(html, "lxml")

# 查找 _clickable-image-container fit-inner 元素
print("查找 _clickable-image-container fit-inner 元素:")
image_containers = soup.select("._clickable-image-container.fit-inner")
print(f"找到 {len(image_containers)} 个元素")

# 分析每个容器的结构
for i, container in enumerate(image_containers):
    print(f"\n容器 {i+1}:")
    print(container.prettify())
    
    # 查找容器内的图片
    imgs = container.select("img")
    print(f"  包含 {len(imgs)} 个图片")
    for j, img in enumerate(imgs):
        print(f"  图片 {j+1}: {img.get('src')}")

# 查找其他可能的图片容器
print("\n查找其他可能的图片容器:")
other_containers = soup.select(".image-container, .img-container, .illustration")
for i, container in enumerate(other_containers):
    print(f"\n容器 {i+1}:")
    print(f"  类: {container.get('class', [])}")
    imgs = container.select("img")
    print(f"  包含 {len(imgs)} 个图片")
    if imgs:
        print(f"  第一个图片: {imgs[0].get('src')}")
