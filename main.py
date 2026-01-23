import random
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.crawlers.crawler_factory import CrawlerFactory
from src.utils.llm_client import LLMClient
from src.push.wechat_push_service import WeChatPushService
from src.scheduler.schedule_manager import ScheduleManager


class WeChatAutoPush:
    def __init__(self):
        self.config = Config()
        self.anime_crawler = None
        self.image_crawler = None
        self.llm_client = None
        self.push_service = None
        self.schedule_manager = None

        self._initialize_components()

    def _initialize_components(self):
        # 初始化爬虫
        anime_sources = self.config.get_anime_sources()
        if anime_sources:
            self.anime_crawler = CrawlerFactory.create_crawler("anime", anime_sources)

        image_sources = self.config.get_image_sources()
        if image_sources:
            self.image_crawler = CrawlerFactory.create_crawler("image", image_sources)

        # 初始化LLM客户端
        llm_config = self.config.get_llm_config()
        if llm_config.get("enabled"):
            self.llm_client = LLMClient(llm_config)

        # 初始化推送服务
        self.push_service = WeChatPushService(self.config)

        # 初始化调度器
        self.schedule_manager = ScheduleManager(self.config, self._run_push_task)

    def _run_push_task(self):
        """执行推送任务"""
        print("开始执行推送任务...")

        # 随机选择推送类型
        content_types = self.config.get_push_config().get(
            "content_types", ["text", "image"]
        )
        content_type = random.choice(content_types)

        # 生成clientmsgid以避免重复推送
        import uuid

        clientmsgid = str(uuid.uuid4())

        if content_type == "text":
            # 爬取动漫新闻
            news = self.anime_crawler.crawl() if self.anime_crawler else None

            if news:
                # 使用LLM改写内容
                if self.llm_client:
                    rewritten_content = self.llm_client.rewrite_content(news["title"])
                    news["content"] = rewritten_content

                # 推送新闻
                result = self.push_service.push_news_article(
                    news["title"],
                    news.get("content", news["title"]),
                    "",  # 可以添加默认图片
                    news["url"],
                    clientmsgid=clientmsgid,
                    send_ignore=False,  # 是否忽略原创校验
                )
                print(f"推送新闻结果: {result}")
            else:
                print("未爬取到新闻内容")

        elif content_type == "image":
            # 爬取图片
            image = self.image_crawler.crawl() if self.image_crawler else None

            if image:
                # 推送图片
                result = self.push_service.push_image_content(
                    image["url"], image.get("alt", "动漫图片"), clientmsgid=clientmsgid
                )
                print(f"推送图片结果: {result}")
            else:
                print("未爬取到图片内容")

        print("推送任务执行完成")

    def run_once(self):
        """立即执行一次推送任务"""
        return self.schedule_manager.run_once()

    def start_schedule(self):
        """启动调度器，开始定时执行任务"""
        self.schedule_manager.start()

    def stop_schedule(self):
        """停止调度器"""
        self.schedule_manager.stop()


if __name__ == "__main__":
    app = WeChatAutoPush()

    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            # 立即执行一次
            app.run_once()
        elif sys.argv[1] == "start":
            # 启动调度器
            app.start_schedule()
        elif sys.argv[1] == "stop":
            # 停止调度器
            app.stop_schedule()
        else:
            print("未知命令，请使用: run, start, stop")
    else:
        # 默认启动调度器
        print("启动微信公众号自动推送程序...")
        app.start_schedule()
