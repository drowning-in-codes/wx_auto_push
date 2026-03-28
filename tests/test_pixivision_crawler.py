from src.crawlers.pixivision_crawler import PixivisionCrawler

# 创建爬虫实例
crawler = PixivisionCrawler(["https://www.pixivision.net/zh/c/illustration"])

# 测试爬取插画列表
try:
    # 爬取第1页
    illustrations = crawler.crawl_pages("https://www.pixivision.net/zh/c/illustration", 1, 1)
    print(f"成功爬取到 {len(illustrations)} 个插画")
    
    # 打印每个插画的信息
    for i, illustration in enumerate(illustrations, 1):
        print(f"\n插画 {i}:")
        print(f"标题: {illustration['title']}")
        print(f"URL: {illustration['url']}")
        print(f"图片URL: {illustration['image_url']}")
        print(f"标签: {', '.join(illustration['tags'])}")
        print(f"来源: {illustration['source']}")
        
except Exception as e:
    print(f"爬取失败: {e}")
    import traceback
    traceback.print_exc()
