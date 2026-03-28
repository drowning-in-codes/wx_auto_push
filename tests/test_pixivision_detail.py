from bs4 import BeautifulSoup
from src.crawlers.pixivision_crawler import PixivisionCrawler

# 创建爬虫实例
crawler = PixivisionCrawler(["https://www.pixivision.net/zh/c/illustration"])

# 测试获取插画详情
try:
    # 测试获取指定插画的详情
    test_url = "https://www.pixivision.net/zh/a/11512"  # 红色主题插画特辑

    # 从本地文件读取 HTML
    with open("pixivision_detail.html", "r", encoding="utf-8") as f:
        response_text = f.read()
    print("已从本地文件读取 HTML")

    # 分析页面结构
    soup = BeautifulSoup(response_text, "lxml")

    # 查找标题
    print("\n查找标题:")
    title_selectors = [".article-header__title", "h1", "h2", ".title"]
    for selector in title_selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        if elements:
            print(f"标题内容: {elements[0].text.strip()}")

    # 查找内容
    print("\n查找内容:")
    content_selectors = [
        ".article-body",
        ".content",
        "p",
        ".article-content",
        ".article-main",
    ]
    for selector in content_selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        if elements:
            print(f"第一个内容元素: {elements[0].text.strip()[:100]}...")

    # 查找主要内容容器
    print("\n查找主要内容容器:")
    main_selectors = ["main", ".main-content", ".article-container"]
    for selector in main_selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        if elements:
            # 查找容器内的 p 标签
            p_elements = elements[0].select("p")
            print(f"  包含 {len(p_elements)} 个 p 元素")
            if p_elements:
                print(f"  第一个 p 元素: {p_elements[0].text.strip()[:100]}...")

    # 查找图片
    print("\n查找图片:")
    img_selectors = [".article-body img", "img"]
    for selector in img_selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        if elements:
            for i, img in enumerate(elements[:3]):
                print(f"图片 {i+1}: {img.get('src')}")

    # 查找标签
    print("\n查找标签:")
    tag_selectors = [".tag-item", ".tag", ".tags", ".tls__list-item"]
    for selector in tag_selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        if elements:
            print(f"标签内容: {[tag.text.strip() for tag in elements[:5]]}")

    # 解析详情
    detail = crawler._parse_illustration_detail(response_text, test_url)

    print("\n解析结果:")
    print(f"标题: '{detail['title']}'")
    print(f"URL: {detail['url']}")
    print(f"内容: '{detail['content'][:200]}'...")  # 只显示前200个字符
    print(f"图片数量: {len(detail['images'])}")
    print(f"标签: {detail['tags']}")
    print(f"来源: {detail['source']}")

except Exception as e:
    print(f"获取详情失败: {e}")
    import traceback

    traceback.print_exc()
