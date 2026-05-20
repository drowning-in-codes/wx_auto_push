#!/usr/bin/env python3
"""
测试代理池功能
"""
import os
import sys
import logging
from src.utils.config import Config
from src.utils.proxy_pool_service import ProxyPoolService
from src.crawlers.crawler_factory import CrawlerFactory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_proxy_pool():
    """测试代理池功能"""
    print("测试代理池功能")
    
    # 加载配置
    config = Config()
    
    # 测试1: 测试代理池服务
    print("\n=== 测试1: 测试代理池服务 ===")
    proxy_pool_config = config.get_proxy_pool_config()
    proxy_pool = ProxyPoolService(proxy_pool_config)
    
    # 获取代理
    print("获取代理...")
    proxy = proxy_pool.get_proxy()
    if proxy:
        print(f"成功获取代理: {proxy}")
    else:
        print("未获取到代理")
    
    # 获取所有代理
    print("获取所有代理...")
    proxies = proxy_pool.get_proxies()
    print(f"代理列表: {proxies}")
    print(f"代理数量: {len(proxies)}")
    
    # 测试2: 测试爬虫使用代理池
    print("\n=== 测试2: 测试爬虫使用代理池 ===")
    test_url = "https://www.pixivision.net/zh/c/illustration"
    
    # 创建爬虫
    crawler = CrawlerFactory.create_crawler(
        "pixivision", 
        [test_url], 
        proxy_config=config.get_proxy_config(),
        request_config=config.get_request_config(),
        proxy_pool_config=proxy_pool_config
    )
    
    # 测试获取代理
    print("测试爬虫获取代理...")
    proxies = crawler._get_proxies()
    if proxies:
        print(f"爬虫成功获取代理: {proxies}")
    else:
        print("爬虫未获取到代理")
    
    # 测试爬取
    print("测试爬取...")
    try:
        result = crawler.crawl()
        if result:
            print(f"爬取成功，获取到 {len(result.get('images', []))} 张图片")
        else:
            print("爬取失败")
    except Exception as e:
        print(f"爬取过程中出错: {e}")

if __name__ == "__main__":
    test_proxy_pool()
