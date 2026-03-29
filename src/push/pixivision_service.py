import os
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.crawlers.crawler_factory import CrawlerFactory
from src.utils.storage.storage_factory import StorageFactory

logger = logging.getLogger(__name__)


class PixivisionService:
    def __init__(
        self,
        proxy_config=None,
        request_config=None,
        storage_type="json",
        **storage_kwargs,
    ):
        """
        初始化 Pixivision 服务
        :param proxy_config: 代理配置
        :param request_config: 请求配置
        :param storage_type: 存储类型，可选值: 'json', 'database'
        :param storage_kwargs: 存储服务的参数
        """
        self.base_url = "https://www.pixivision.net/zh/c/illustration"
        self.proxy_config = proxy_config
        self.request_config = request_config
        self.crawler = CrawlerFactory.create_crawler(
            "pixivision", [self.base_url], proxy_config, request_config
        )
        # 初始化存储服务
        self.storage = StorageFactory.create_storage(storage_type, **storage_kwargs)

    def get_illustration_list(self, start_page=1, end_page=1, save=False, query=None):
        """
        获取插画列表
        :param start_page: 开始页码
        :param end_page: 结束页码
        :param save: 是否保存到存储
        :param query: 搜索关键词
        :return: 插画列表
        """
        # 如果有搜索关键词，使用搜索页面的URL
        if query:
            search_url = "https://www.pixivision.net/zh/s/"
            illustrations = self.crawler.crawl_pages(
                search_url, start_page, end_page, query
            )
        else:
            # 否则使用默认的URL
            illustrations = self.crawler.crawl_pages(
                self.base_url, start_page, end_page, query
            )
        if save and self.storage:
            self.save_illustrations(illustrations)
        return illustrations

    def get_illustration_detail(self, illustration_url, save=False):
        """
        获取单个插画详情
        :param illustration_url: 插画详情页URL
        :param save: 是否保存到存储
        :return: 插画详情
        """
        # 创建一个临时爬虫实例来爬取详情页
        detail_crawler = CrawlerFactory.create_crawler(
            "pixivision", [illustration_url], self.proxy_config, self.request_config
        )
        illustration = detail_crawler.crawl()
        if save and self.storage and illustration:
            self.save_illustration(illustration)
        return illustration

    def get_ranking(self, save=False):
        """
        获取排行榜（第一个 sidebar-contents-container）
        :param save: 是否保存到存储
        :return: 排行榜插画列表
        """
        ranking_url = "https://www.pixivision.net/zh/"
        ranking_crawler = CrawlerFactory.create_crawler(
            "pixivision", [ranking_url], self.proxy_config, self.request_config
        )
        # 直接调用 _parse_ranking_list 方法并指定容器索引为 0（排行榜）
        response = ranking_crawler.session.get(
            ranking_url,
            headers=ranking_crawler._get_headers(),
            proxies=ranking_crawler._get_proxies(),
        )
        response.raise_for_status()
        illustrations = ranking_crawler._parse_ranking_list(
            response.text, ranking_url, 0
        )
        if save and self.storage:
            self.save_illustrations(illustrations)
        return illustrations

    def get_recommendations(self, save=False):
        """
        获取推荐榜（第二个 sidebar-contents-container）
        :param save: 是否保存到存储
        :return: 推荐榜插画列表
        """
        ranking_url = "https://www.pixivision.net/zh/"
        ranking_crawler = CrawlerFactory.create_crawler(
            "pixivision", [ranking_url], self.proxy_config, self.request_config
        )
        # 直接调用 _parse_ranking_list 方法并指定容器索引为 1（推荐榜）
        response = ranking_crawler.session.get(
            ranking_url,
            headers=ranking_crawler._get_headers(),
            proxies=ranking_crawler._get_proxies(),
        )
        response.raise_for_status()
        illustrations = ranking_crawler._parse_ranking_list(
            response.text, ranking_url, 1
        )
        if save and self.storage:
            self.save_illustrations(illustrations)
        return illustrations

    def download_illustration_images(
        self,
        illustration_id,
        download_dir,
        max_retries=3,
        max_workers=5,
    ):
        """
        下载插画图片到指定目录

        :param illustration_id: 插画ID
        :param download_dir: 下载目录
        :param max_retries: 最大重试次数
        :param max_workers: 最大线程数
        :return: (success, download_path, downloaded_files) 成功状态、下载路径、下载的文件列表
        """
        # 获取插画详情
        illustration_url = f"https://www.pixivision.net/zh/a/{illustration_id}"
        logger.info(f"获取插画详情: {illustration_url}")
        illustration = self.get_illustration_detail(illustration_url)

        if not illustration:
            logger.error(f"获取插画 {illustration_id} 详情失败")
            return False, None, []

        title = illustration.get("title", f"illustration_{illustration_id}")
        images = illustration.get("images", [])

        if not images:
            logger.error(f"插画 {illustration_id} 没有图片")
            return False, None, []

        # 清理标题，确保可以作为文件夹名称
        safe_title = "".join(
            c for c in title if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        if not safe_title:
            safe_title = f"illustration_{illustration_id}"

        # 创建下载目录
        download_path = os.path.join(download_dir, safe_title)
        os.makedirs(download_path, exist_ok=True)

        logger.info(f"开始下载插画 {illustration_id} 的图片到: {download_path}")
        logger.info(f"共 {len(images)} 张图片")

        downloaded_files = []

        def download_single_image(image_url, index, total):
            """下载单张图片"""
            for attempt in range(max_retries):
                try:
                    # 添加请求延迟（第一次不延迟）
                    if index > 0 and self.request_config:
                        delay = self.request_config.get("delay", 1)
                        if delay > 0:
                            time.sleep(delay)

                    logger.info(
                        f"下载图片 {index+1}/{total}: {image_url} "
                        f"(尝试 {attempt+1}/{max_retries})"
                    )

                    # 配置代理
                    proxies = None
                    if self.proxy_config and self.proxy_config.get("enabled", False):
                        http_proxy = self.proxy_config.get("http_proxy", "")
                        https_proxy = self.proxy_config.get("https_proxy", "")
                        if http_proxy or https_proxy:
                            proxies = {
                                "http": http_proxy,
                                "https": https_proxy,
                            }
                    else:
                        # 显式禁用代理，覆盖系统环境中的代理配置
                        os.environ["HTTP_PROXY"] = ""
                        os.environ["HTTPS_PROXY"] = ""

                    # 下载图片
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                    }
                    response = requests.get(
                        image_url, timeout=30, proxies=proxies, headers=headers
                    )
                    response.raise_for_status()

                    # 获取文件扩展名
                    ext = os.path.splitext(image_url.split("?")[0])[1]
                    if not ext:
                        ext = ".jpg"

                    # 保存图片
                    file_name = f"{index+1:03d}{ext}"
                    file_path = os.path.join(download_path, file_name)

                    with open(file_path, "wb") as f:
                        f.write(response.content)

                    logger.info(f"图片 {index+1}/{total} 下载成功: {file_name}")
                    return True, file_path

                except Exception as e:
                    logger.error(
                        f"图片 {index+1}/{total} 下载失败 "
                        f"(尝试 {attempt+1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        retry_delay = 2**attempt
                        logger.info(f"等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"图片 {index+1}/{total} 超过最大重试次数，跳过")
                        return False, None

            return False, None

        # 使用多线程下载
        actual_max_workers = min(max_workers, len(images))
        logger.info(f"使用 {actual_max_workers} 个线程下载")

        executor = ThreadPoolExecutor(max_workers=actual_max_workers)
        future_to_index = {
            executor.submit(download_single_image, image_url, i, len(images)): i
            for i, image_url in enumerate(images)
        }

        try:
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    success, file_path = future.result()
                    if success and file_path:
                        downloaded_files.append(file_path)
                    else:
                        logger.warning(f"图片 {index+1}/{len(images)} 下载失败")
                except Exception as e:
                    logger.error(f"图片 {index+1}/{len(images)} 处理异常: {e}")
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止下载...")
            executor.shutdown(wait=False)  # 立即关闭线程池，不等待所有任务完成
            raise  # 重新抛出异常，让调用方知道下载被中断
        finally:
            executor.shutdown(wait=False)

        logger.info(f"下载完成: 成功 {len(downloaded_files)}/{len(images)} 张")

        if downloaded_files:
            return True, download_path, downloaded_files
        else:
            return False, download_path, []

    def save_illustration(self, illustration):
        """
        保存单个插画信息
        :param illustration: 插画信息
        :return: 保存结果
        """
        if self.storage:
            return self.storage.save_illustration(illustration)
        return False

    def save_illustrations(self, illustrations):
        """
        批量保存插画信息
        :param illustrations: 插画列表
        :return: 保存结果
        """
        if self.storage:
            return self.storage.save_illustrations(illustrations)
        return False

    def get_stored_illustration(self, article_id):
        """
        从存储中获取插画信息
        :param article_id: 文章ID
        :return: 插画信息
        """
        if self.storage:
            return self.storage.get_illustration(article_id)
        return None

    def get_stored_illustrations(self, limit=100, offset=0):
        """
        从存储中获取插画列表
        :param limit: 返回数量限制
        :param offset: 偏移量
        :return: 插画列表
        """
        if self.storage:
            return self.storage.get_illustrations(limit, offset)
        return []

    def search_illustrations(self, keyword, limit=100):
        """
        搜索插画
        :param keyword: 搜索关键词
        :param limit: 返回数量限制
        :return: 搜索结果
        """
        if self.storage:
            return self.storage.search_illustrations(keyword, limit)
        return []

    def get_illustration_by_id(self, illustration_id, save=False):
        """
        根据ID获取插画详情
        :param illustration_id: 插画ID
        :param save: 是否保存到存储
        :return: 插画详情
        """
        illustration_url = f"https://www.pixivision.net/zh/a/{illustration_id}"
        return self.get_illustration_detail(illustration_url, save)

    def get_random_article_id(self, start_page=1, end_page=3, exclude_ids=None):
        """
        随机获取一个article id
        :param start_page: 开始页码
        :param end_page: 结束页码
        :param exclude_ids: 要排除的article id列表
        :return: 随机选择的article id，如果没有可用的返回None
        """
        if exclude_ids is None:
            exclude_ids = set()
        else:
            exclude_ids = set(exclude_ids)

        try:
            # 获取插画列表
            illustrations = self.get_illustration_list(start_page, end_page, save=False)

            if not illustrations:
                logger.warning("没有获取到插画列表")
                return None

            # 过滤掉已排除的article id和空/缺失的article_id
            available_illustrations = [
                ill
                for ill in illustrations
                if ill.get("article_id") and ill.get("article_id") not in exclude_ids
            ]

            if not available_illustrations:
                logger.warning("没有可用的插画（所有插画都已排除）")
                return None

            # 随机选择一个
            import random

            selected = random.choice(available_illustrations)
            article_id = selected.get("article_id")

            logger.info(f"随机选择了article id: {article_id}")
            return article_id

        except Exception as e:
            logger.error(f"随机获取article id失败: {e}")
            return None
