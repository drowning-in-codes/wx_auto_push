#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号自动推送工具
支持定时推送、模板消息、图片消息等功能
"""

import os
import sys
import time
import argparse
import threading
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.utils.db_manager import DBManager
from src.crawlers.crawler_factory import CrawlerFactory
from src.push.wechat_push_service import WeChatPushService
from src.push.pixivision_service import PixivisionService
from src.scheduler.schedule_manager import ScheduleManager
from src.push.wechat_callback_server import WeChatCallbackServer
from src.utils.llm_client import LLMClient


class WeChatAutoPush:
    def __init__(self):
        self.config = Config()
        self.anime_crawler = None
        self.image_crawler = None
        self.llm_client = None
        self.push_service = None
        self.wechat_draft_service = None
        self.draft_service = None
        self.schedule_manager = None
        self.db_manager = DBManager()
        self.callback_server = None
        self.pixivision_service = None

        self._initialize_components()
        self._initialize_callback_server()

    def _initialize_components(self):
        # 初始化爬虫
        anime_sources = self.config.get_anime_sources()
        proxy_config = self.config.get_proxy_config()
        if anime_sources:
            self.anime_crawler = CrawlerFactory.create_crawler(
                "anime", anime_sources, proxy_config
            )

        image_sources = self.config.get_image_sources()
        if image_sources:
            self.image_crawler = CrawlerFactory.create_crawler(
                "image", image_sources, proxy_config
            )

        # 初始化LLM客户端
        llm_config = self.config.get_llm_config()
        if llm_config.get("enabled"):
            self.llm_client = LLMClient(llm_config, proxy_config)

        # 初始化推送服务
        self.push_service = WeChatPushService(self.config)

        # 初始化微信草稿服务
        from src.push.wechat_draft_service import WeChatDraftService
        from src.push.wechat_client import WeChatClient

        wechat_config = self.config.get_wechat_config()
        proxy_config = self.config.get_proxy_config()
        wechat_client = WeChatClient(
            wechat_config.get("app_id"), wechat_config.get("app_secret"), proxy_config
        )
        self.wechat_draft_service = WeChatDraftService(wechat_client)

        # 初始化 Pixivision 服务
        proxy_config = self.config.get_proxy_config()
        # 初始化 Pixivision 服务（使用JSON存储）
        self.pixivision_service = PixivisionService(
            proxy_config=proxy_config,
            request_config=self.config.get_request_config(),
            storage_type="json",
            file_path="data/illustrations.json",
        )

        # 初始化草稿服务
        from src.push.draft_service import DownloadAndDraftService

        self.draft_service = DownloadAndDraftService(
            self.push_service,
            self.wechat_draft_service,
            self.pixivision_service,
            self.config,
        )

        # 初始化调度器
        self.schedule_manager = ScheduleManager(self.config, self._run_push_task)

    def save_wechat_config(self, config_data):
        """
        保存微信公众号配置到 .env 文件
        """
        # 读取现有的 .env 文件内容
        env_file = ".env"
        existing_lines = []
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()

        # 创建配置映射
        config_map = {
            "app_id": "WECHAT_APP_ID",
            "app_secret": "WECHAT_APP_SECRET",
            "template_id": "WECHAT_TEMPLATE_ID",
            "preview_openid": "WECHAT_PREVIEW_OPENID",
        }

        # 更新或添加配置
        updated_lines = []
        for line in existing_lines:
            line = line.strip()
            if not line or line.startswith("#"):
                updated_lines.append(line)
                continue

            key = line.split("=")[0].strip()
            if key in config_map.values():
                # 跳过现有配置，稍后统一添加
                continue
            updated_lines.append(line)

        # 添加新配置
        for key, env_key in config_map.items():
            if key in config_data:
                updated_lines.append(f"{env_key}={config_data[key]}")

        # 写入更新后的配置
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines) + "\n")

        print("微信公众号配置已保存")

    def _initialize_callback_server(self):
        """
        初始化回调服务器
        """
        wechat_config = self.config.get_wechat_config()
        callback_config = wechat_config.get("callback", {})
        if callback_config.get("enabled"):
            self.callback_server = WeChatCallbackServer(
                config=self.config,
                db_manager=self.db_manager,
                push_service=self.push_service,
            )
            # 启动回调服务器
            self.callback_server.run()
            print("微信回调服务器已启动")

    def _run_push_task(self):
        """
        运行推送任务
        """
        try:
            push_config = self.config.get_push_config()
            push_type = push_config.get("type", "text")

            if push_type == "text":
                self.push_text_message()
            elif push_type == "image":
                self.push_image_message()
            elif push_type == "news":
                self.push_news_message()
            elif push_type == "template":
                self.push_template_message()
            elif push_type == "pixivision":
                self.push_pixivision_illustration()
            else:
                print(f"不支持的推送类型: {push_type}")
        except Exception as e:
            print(f"运行推送任务时出错: {e}")

    def push_text_message(self, content=None):
        """
        推送文本消息
        """
        if content is None:
            content = "这是一条测试消息"
        self.push_service.send_text_message(content)

    def push_image_message(self, image_path=None):
        """
        推送图片消息
        """
        if image_path is None:
            # 默认使用第一张图片
            image_sources = self.config.get_image_sources()
            if image_sources and self.image_crawler:
                images = self.image_crawler.crawl()
                if images:
                    image_path = images[0]
        if image_path:
            self.push_service.send_image_message(image_path)
        else:
            print("没有可用的图片")

    def push_news_message(self):
        """
        推送图文消息
        """
        # 示例：创建一个简单的图文消息
        articles = [
            {
                "title": "测试图文消息",
                "description": "这是一条测试图文消息",
                "url": "https://www.example.com",
                "picurl": "https://www.example.com/image.jpg",
            }
        ]
        self.push_service.send_news_message(articles)

    def push_template_message(self, data=None):
        """
        推送模板消息
        """
        if data is None:
            data = {
                "keyword1": {"value": "测试内容"},
                "keyword2": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            }
        self.push_service.send_template_message(data)

    def push_pixivision_illustration(self):
        """
        推送 Pixivision 插画
        """
        try:
            # 爬取 Pixivision 插画
            illustrations = self.pixivision_service.get_latest_illustrations()
            if not illustrations:
                print("没有获取到插画")
                return

            # 推送第一张插画
            illustration = illustrations[0]
            print(f"推送插画: {illustration.get('title')}")

            # 下载图片
            image_url = (
                illustration.get("thumbnail") or illustration.get("images", [])[0]
            )
            if image_url:
                # 推送图片消息
                self.push_service.send_image_message_from_url(image_url)
            else:
                print("没有图片URL")
        except Exception as e:
            print(f"推送 Pixivision 插画失败: {e}")

    def download_pixivision_illustration(self, illustration_id, output_dir=None):
        """
        下载 Pixivision 插画图片

        :param illustration_id: 插画ID
        :param output_dir: 输出目录（可选，默认使用配置文件中的目录）
        """
        try:
            # 获取下载目录
            if output_dir is None:
                output_dir = self.config.get_download_directory()

            # 获取下载配置
            download_config = self.config.get_download_config()
            max_workers = download_config.get("max_workers", 5)
            max_retries = download_config.get("max_retries", 3)

            print(f"开始下载插画 {illustration_id} 的图片...")
            print(f"输出目录: {output_dir}")

            # 下载图片
            success, download_path, downloaded_files = (
                self.pixivision_service.download_illustration_images(
                    illustration_id,
                    output_dir,
                    max_retries=max_retries,
                    max_workers=max_workers,
                )
            )

            if success:
                print(f"\n下载成功！")
                print(f"保存路径: {download_path}")
                print(f"下载文件数: {len(downloaded_files)}")
                for file_path in downloaded_files:
                    print(f"  - {os.path.basename(file_path)}")
            else:
                print(f"\n下载失败或未下载到任何图片")
                if download_path:
                    print(f"目标路径: {download_path}")

        except Exception as e:
            print(f"下载 Pixivision 插画失败: {e}")

    def store_pixivision_illustration(self, illustration_id):
        """
        存储 Pixivision 插画信息
        """
        try:
            illustration = self.pixivision_service.get_illustration_by_id(
                illustration_id
            )
            if not illustration:
                print(f"获取插画 {illustration_id} 失败")
                return

            # 保存插画信息
            success = self.pixivision_service.save_illustration(illustration)
            if success:
                print(f"插画 {illustration_id} 存储成功")
            else:
                print(f"插画 {illustration_id} 存储失败")
        except Exception as e:
            print(f"存储 Pixivision 插画失败: {e}")

    def get_stored_pixivision_illustrations(self, limit=10, offset=0):
        """
        获取已存储的 Pixivision 插画
        """
        try:
            illustrations = self.pixivision_service.get_stored_illustrations(
                limit, offset
            )
            if not illustrations:
                print("没有存储的插画")
                return

            print(f"共找到 {len(illustrations)} 张存储的插画:")
            for i, illustration in enumerate(illustrations, 1):
                print(
                    f"{i}. {illustration.get('title')} (ID: {illustration.get('article_id')})"
                )
                print(f"   URL: {illustration.get('url')}")
                print(f"   标签: {', '.join(illustration.get('tags', []))}")
                print()
        except Exception as e:
            print(f"获取存储的 Pixivision 插画失败: {e}")

    def search_pixivision_illustrations(self, keyword, limit=100):
        """
        搜索 Pixivision 插画
        """
        try:
            illustrations = self.pixivision_service.search_illustrations(keyword, limit)
            if not illustrations:
                print(f"没有找到包含 '{keyword}' 的插画")
                return

            print(f"共找到 {len(illustrations)} 张匹配的插画:")
            for i, illustration in enumerate(illustrations, 1):
                print(
                    f"{i}. {illustration.get('title')} (ID: {illustration.get('article_id')})"
                )
                print(f"   URL: {illustration.get('url')}")
                print(f"   标签: {', '.join(illustration.get('tags', []))}")
                print()
        except Exception as e:
            print(f"搜索 Pixivision 插画失败: {e}")

    def get_pixivision_illustrations(
        self, start_page=1, end_page=1, save=False, query=None
    ):
        """
        获取 Pixivision 插画列表
        """
        try:
            illustrations = self.pixivision_service.get_illustration_list(
                start_page, end_page, save, query
            )
            if illustrations:
                print(f"找到 {len(illustrations)} 个插画:")
                for i, illustration in enumerate(illustrations, 1):
                    print(f"\n{i}. {illustration.get('title')}")
                    print(f"   URL: {illustration.get('url')}")
                    print(f"   标签: {', '.join(illustration.get('tags', []))}")
                    print(f"   插画ID: {illustration.get('article_id', '未知')}")
            else:
                print("没有找到插画")
        except Exception as e:
            print(f"获取插画列表失败: {e}")

    def get_pixivision_illustration_detail(self, illustration_id, save=False):
        """
        获取 Pixivision 插画详情
        """
        try:
            illustration = self.pixivision_service.get_illustration_by_id(
                illustration_id, save
            )
            if illustration:
                print(f"插画详情:")
                print(f"标题: {illustration.get('title')}")
                print(f"URL: {illustration.get('url')}")
                print(f"插画ID: {illustration.get('article_id', illustration_id)}")
                print(f"描述: {illustration.get('description', '无')}")
                print(f"标签: {', '.join(illustration.get('tags', []))}")
                print(f"图片数量: {len(illustration.get('images', []))}")
            else:
                print("没有找到插画详情")
        except Exception as e:
            print(f"获取插画详情失败: {e}")

    def get_pixivision_ranking(self, save=False):
        """
        获取 Pixivision 排行榜
        """
        try:
            illustrations = self.pixivision_service.get_ranking(save)
            if illustrations:
                print(f"排行榜 (共 {len(illustrations)} 个插画):")
                for i, illustration in enumerate(illustrations, 1):
                    print(f"\n{i}. {illustration.get('title')}")
                    print(f"   URL: {illustration.get('url')}")
                    print(f"   插画ID: {illustration.get('article_id', '未知')}")
            else:
                print("没有找到排行榜数据")
        except Exception as e:
            print(f"获取排行榜失败: {e}")

    def get_pixivision_recommendations(self, save=False):
        """
        获取 Pixivision 推荐榜
        """
        try:
            illustrations = self.pixivision_service.get_recommendations(save)
            if illustrations:
                print(f"推荐榜 (共 {len(illustrations)} 个插画):")
                for i, illustration in enumerate(illustrations, 1):
                    print(f"\n{i}. {illustration.get('title')}")
                    print(f"   URL: {illustration.get('url')}")
                    print(f"   插画ID: {illustration.get('article_id', '未知')}")
            else:
                print("没有找到推荐榜数据")
        except Exception as e:
            print(f"获取推荐榜失败: {e}")

    def get_stored_pixivision_illustration(self, illustration_id):
        """
        从存储中获取 Pixivision 插画
        """
        try:
            illustration = self.pixivision_service.get_stored_illustration(
                illustration_id
            )
            if illustration:
                print(f"插画详情:")
                print(f"标题: {illustration.get('title')}")
                print(f"URL: {illustration.get('url')}")
                print(f"插画ID: {illustration.get('article_id', '未知')}")
                print(f"描述: {illustration.get('description', '无')}")
                print(f"标签: {', '.join(illustration.get('tags', []))}")
                print(f"图片数量: {len(illustration.get('images', []))}")
            else:
                print("没有找到存储的插画")
        except Exception as e:
            print(f"获取存储的插画失败: {e}")

    def set_schedule_time(self, start, end):
        """
        设置推送时间范围
        """
        try:
            self.config.set_push_time_range(start, end)
            print(f"推送时间范围已设置为: {start} - {end}")
        except Exception as e:
            print(f"设置时间范围失败: {e}")

    def set_schedule_frequency(self, weekly_frequency):
        """
        设置推送频率
        """
        try:
            self.config.set_weekly_push_frequency(weekly_frequency)
            print(f"每周推送频率已设置为: {weekly_frequency} 次")
        except Exception as e:
            print(f"设置推送频率失败: {e}")

    def view_schedule_config(self):
        """
        查看当前调度配置
        """
        try:
            config = self.config.get_schedule_config()
            time_range = config.get("time_range", {})
            start_time = time_range.get("start")
            end_time = time_range.get("end")

            print("当前调度配置:")
            print(f"推送时间范围: {start_time} - {end_time}")
            print(f"每周推送频率: {config.get('weekly_frequency')} 次")
            print(f"推送类型: {config.get('push_type')}")
            print(f"是否启用推送: {'是' if config.get('enable_push') else '否'}")
        except Exception as e:
            print(f"查看调度配置失败: {e}")

    def draft_switch(self, checkonly=0):
        """
        草稿箱开关设置
        """
        result = self.wechat_draft_service.draft_switch(checkonly)
        if result:
            print(f"草稿箱开关设置成功: {result}")
        else:
            print("草稿箱开关设置失败")

    def draft_add(
        self, title, author, content, digest, thumb_media_id, show_cover_pic=1
    ):
        """
        新增草稿
        """
        articles = [
            {
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": show_cover_pic,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
        result = self.wechat_draft_service.draft_add(articles)
        if result:
            print(f"新增草稿成功: {result}")
        else:
            print("新增草稿失败")

    def draft_list(self, offset=0, count=20):
        """
        获取草稿列表
        """
        result = self.wechat_draft_service.draft_batchget(offset, count)
        if result and "item" in result:
            print(f"共找到 {len(result['item'])} 条草稿:")
            for i, draft in enumerate(result["item"], 1):
                print(f"{i}. {draft.get('title')} (ID: {draft.get('media_id')})")
                print(f"   作者: {draft.get('author')}")
                print(
                    f"   更新时间: {datetime.fromtimestamp(draft.get('update_time')).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print()
        else:
            print("获取草稿列表失败")

    def draft_count(self):
        """
        获取草稿总数
        """
        result = self.wechat_draft_service.draft_count()
        if result and "total_count" in result:
            print(f"草稿总数: {result['total_count']}")
        else:
            print("获取草稿总数失败")

    def draft_delete(self, media_id):
        """
        删除草稿
        """
        result = self.wechat_draft_service.draft_delete(media_id)
        if result:
            print(f"删除草稿成功: {result}")
        else:
            print("删除草稿失败")

    def draft_get(self, media_id):
        """
        获取草稿详情
        """
        result = self.wechat_draft_service.get_draft(media_id)
        if result and "news_item" in result:
            print(f"草稿详情:")
            for i, item in enumerate(result["news_item"], 1):
                print(f"{i}. {item.get('title')}")
                print(f"   作者: {item.get('author')}")
                print(f"   摘要: {item.get('digest')}")
                print(f"   封面: {item.get('thumb_media_id')}")
                print()
        else:
            print("获取草稿详情失败")

    def draft_update(
        self,
        media_id,
        index,
        title,
        author,
        content,
        digest,
        thumb_media_id,
        show_cover_pic=1,
    ):
        """
        更新草稿
        """
        articles = [
            {
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": show_cover_pic,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
        result = self.wechat_draft_service.draft_update(media_id, index, articles)
        if result:
            print(f"更新草稿成功: {result}")
        else:
            print("更新草稿失败")

    def draft_submit(self, media_id, title=None):
        """
        发布草稿
        """
        result = self.wechat_draft_service.draft_submit(media_id, title)
        if result and "publish_id" in result:
            print(f"发布草稿成功: {result}")
        else:
            print("发布草稿失败")

    def draft_create(
        self,
        source,
        title=None,
        author=None,
        compress=None,
        digest=None,
        content=None,
        show_cover=1,
        message_type="news",
    ):
        """
        上传图片并创建草稿

        参数:
            source: 图片来源，本地文件夹路径或Pixivision文章ID
            title: 草稿标题
            author: 作者名称
            compress: 是否压缩图片
            digest: 图文消息摘要
            content: 图文消息内容
            show_cover: 是否显示封面图片
            message_type: 消息类型，news(图文消息)或newspic(图片消息)
        """
        self.draft_service.create_draft(
            source,
            title,
            author,
            compress,
            digest,
            content,
            show_cover,
            message_type,
        )

    def run(self):
        """
        运行自动推送服务
        """
        print("微信公众号自动推送服务启动")
        print("按 Ctrl+C 停止服务")

        try:
            # 启动调度器
            self.schedule_manager.start()
        except KeyboardInterrupt:
            print("服务已停止")
            self.schedule_manager.stop()

    def run_schedule(self):
        """
        启动调度推送
        """
        self.run()

    def run_once(self):
        """
        执行一次推送后关闭
        """
        try:
            print("执行一次推送...")
            # 直接执行推送任务
            self._run_push_task()
            print("推送执行完成，服务已关闭")
        except Exception as e:
            print(f"执行推送失败: {e}")

    def handle_message(self, message):
        """
        处理接收到的消息
        """
        print(f"接收到消息: {message}")
        # 这里可以添加消息处理逻辑


def main():
    parser = argparse.ArgumentParser(description="微信公众号自动推送工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 推送相关命令
    push_parser = subparsers.add_parser("push", help="推送消息")
    push_parser.add_argument(
        "type",
        choices=["text", "image", "news", "template", "pixivision"],
        help="推送类型",
    )

    # 配置相关命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_parser.add_argument("action", choices=["set"], help="配置操作")
    config_parser.add_argument("--app_id", help="微信公众号 App ID")
    config_parser.add_argument("--app_secret", help="微信公众号 App Secret")
    config_parser.add_argument("--template_id", help="模板消息 ID")
    config_parser.add_argument("--preview_openid", help="预览 OpenID")

    # 调度管理命令
    schedule_parser = subparsers.add_parser("schedule", help="调度管理")
    schedule_subparsers = schedule_parser.add_subparsers(
        dest="schedule_command", help="调度管理命令"
    )

    # 设置时间范围
    schedule_time_parser = schedule_subparsers.add_parser(
        "time", help="设置推送时间范围"
    )
    schedule_time_parser.add_argument(
        "--start", required=True, help="开始时间，格式：HH:MM"
    )
    schedule_time_parser.add_argument(
        "--end", required=True, help="结束时间，格式：HH:MM"
    )

    # 设置频率
    schedule_frequency_parser = schedule_subparsers.add_parser(
        "frequency", help="设置推送频率"
    )
    schedule_frequency_parser.add_argument(
        "weekly_frequency", type=int, help="每周推送次数"
    )

    # 查看当前调度配置
    schedule_view_parser = schedule_subparsers.add_parser(
        "view", help="查看当前调度配置"
    )

    # 启动调度推送
    schedule_run_parser = schedule_subparsers.add_parser("run", help="启动调度推送")

    # 执行一次推送后关闭
    schedule_run_once_parser = schedule_subparsers.add_parser(
        "run-once", help="执行一次推送后关闭"
    )

    # Pixivision 管理命令
    pixivision_parser = subparsers.add_parser("pixivision", help="Pixivision 管理")
    pixivision_subparsers = pixivision_parser.add_subparsers(
        dest="pixivision_command", help="Pixivision 管理命令"
    )

    # 获取插画列表
    pixivision_list_parser = pixivision_subparsers.add_parser(
        "list", help="获取插画列表"
    )
    pixivision_list_parser.add_argument(
        "--start_page", type=int, default=1, help="开始页码"
    )
    pixivision_list_parser.add_argument(
        "--end_page", type=int, default=1, help="结束页码"
    )
    pixivision_list_parser.add_argument(
        "--save", action="store_true", help="是否保存到存储"
    )
    pixivision_list_parser.add_argument("-q", "--query", help="搜索关键词")

    # 获取插画详情
    pixivision_detail_parser = pixivision_subparsers.add_parser(
        "detail", help="获取插画详情"
    )
    pixivision_detail_parser.add_argument("illustration_id", help="插画 ID")
    pixivision_detail_parser.add_argument(
        "--save", action="store_true", help="是否保存到存储"
    )

    # 获取排行榜
    pixivision_ranking_parser = pixivision_subparsers.add_parser(
        "ranking", help="获取排行榜"
    )
    pixivision_ranking_parser.add_argument(
        "--save", action="store_true", help="是否保存到存储"
    )

    # 获取推荐榜
    pixivision_recommendations_parser = pixivision_subparsers.add_parser(
        "recommendations", help="获取推荐榜"
    )
    pixivision_recommendations_parser.add_argument(
        "--save", action="store_true", help="是否保存到存储"
    )

    # 保存插画
    pixivision_save_parser = pixivision_subparsers.add_parser("save", help="保存插画")
    pixivision_save_parser.add_argument("illustration_id", help="插画 ID")

    # 从存储中获取插画
    pixivision_get_parser = pixivision_subparsers.add_parser(
        "get", help="从存储中获取插画"
    )
    pixivision_get_parser.add_argument("illustration_id", help="插画 ID")

    # 查看已存储的插画
    pixivision_stored_parser = pixivision_subparsers.add_parser(
        "stored", help="查看已存储的插画"
    )
    pixivision_stored_parser.add_argument(
        "--limit", type=int, default=10, help="返回数量限制"
    )
    pixivision_stored_parser.add_argument(
        "--offset", type=int, default=0, help="偏移量"
    )

    # 搜索插画
    pixivision_search_parser = pixivision_subparsers.add_parser(
        "search", help="搜索插画"
    )
    pixivision_search_parser.add_argument("keyword", help="搜索关键词")
    pixivision_search_parser.add_argument(
        "--limit", type=int, default=10, help="返回数量限制"
    )

    # 推送 Pixivision 插画
    pixivision_push_parser = pixivision_subparsers.add_parser(
        "push", help="推送 Pixivision 插画"
    )

    # 下载 Pixivision 插画图片
    pixivision_download_parser = pixivision_subparsers.add_parser(
        "download", help="下载 Pixivision 插画图片"
    )
    pixivision_download_parser.add_argument("illustration_id", help="插画ID")
    pixivision_download_parser.add_argument(
        "--output", help="输出目录（默认使用配置文件中的目录）"
    )

    # 草稿管理命令
    draft_parser = subparsers.add_parser("draft", help="草稿管理")
    draft_subparsers = draft_parser.add_subparsers(
        dest="draft_command", help="草稿管理命令"
    )

    # 草稿开关设置
    draft_switch_parser = draft_subparsers.add_parser("switch", help="草稿箱开关设置")
    draft_switch_parser.add_argument(
        "--checkonly", type=int, default=0, help="是否只检查状态"
    )

    # 新增草稿
    draft_add_parser = draft_subparsers.add_parser("add", help="新增草稿")
    draft_add_parser.add_argument("--title", required=True, help="标题")
    draft_add_parser.add_argument("--author", required=True, help="作者")
    draft_add_parser.add_argument("--content", required=True, help="内容")
    draft_add_parser.add_argument("--digest", required=True, help="摘要")
    draft_add_parser.add_argument(
        "--thumb_media_id", required=True, help="封面图片 Media ID"
    )
    draft_add_parser.add_argument(
        "--show_cover_pic", type=int, default=1, help="是否显示封面"
    )

    # 获取草稿列表
    draft_list_parser = draft_subparsers.add_parser("list", help="获取草稿列表")
    draft_list_parser.add_argument("--offset", type=int, default=0, help="偏移量")
    draft_list_parser.add_argument("--count", type=int, default=20, help="数量")

    # 获取草稿总数
    draft_count_parser = draft_subparsers.add_parser("count", help="获取草稿总数")

    # 删除草稿
    draft_delete_parser = draft_subparsers.add_parser("delete", help="删除草稿")
    draft_delete_parser.add_argument("media_id", help="草稿 Media ID")

    # 获取草稿详情
    draft_get_parser = draft_subparsers.add_parser("get", help="获取草稿详情")
    draft_get_parser.add_argument("media_id", help="草稿 Media ID")

    # 更新草稿
    draft_update_parser = draft_subparsers.add_parser("update", help="更新草稿")
    draft_update_parser.add_argument("media_id", help="草稿 Media ID")
    draft_update_parser.add_argument("--index", type=int, default=0, help="文章索引")
    draft_update_parser.add_argument("--title", required=True, help="标题")
    draft_update_parser.add_argument("--author", required=True, help="作者")
    draft_update_parser.add_argument("--content", required=True, help="内容")
    draft_update_parser.add_argument("--digest", required=True, help="摘要")
    draft_update_parser.add_argument(
        "--thumb_media_id", required=True, help="封面图片 Media ID"
    )
    draft_update_parser.add_argument(
        "--show_cover_pic", type=int, default=1, help="是否显示封面"
    )

    # 发布草稿
    draft_submit_parser = draft_subparsers.add_parser("submit", help="发布草稿")
    draft_submit_parser.add_argument("media_id", help="草稿 Media ID")
    draft_submit_parser.add_argument("--title", help="自定义标题")

    # 创建草稿
    draft_create_parser = draft_subparsers.add_parser(
        "create", help="上传图片并创建草稿"
    )
    draft_create_parser.add_argument(
        "source", help="图片来源，本地文件夹路径或Pixivision文章ID"
    )
    draft_create_parser.add_argument("--title", help="草稿标题")
    draft_create_parser.add_argument("--author", help="作者名称")
    draft_create_parser.add_argument("--compress", type=bool, help="是否压缩图片")
    draft_create_parser.add_argument("--digest", help="图文消息摘要")
    draft_create_parser.add_argument("--content", help="图文消息内容")
    draft_create_parser.add_argument(
        "--show_cover", type=int, default=1, help="是否显示封面图片"
    )
    draft_create_parser.add_argument(
        "--message_type",
        choices=["news", "newspic"],
        default="news",
        help="消息类型，news(图文消息)或newspic(图片消息)",
    )

    args = parser.parse_args()

    app = WeChatAutoPush()

    if args.command == "push":
        if args.type == "text":
            app.push_text_message()
        elif args.type == "image":
            app.push_image_message()
        elif args.type == "news":
            app.push_news_message()
        elif args.type == "template":
            app.push_template_message()
        elif args.type == "pixivision":
            app.push_pixivision_illustration()
    elif args.command == "config":
        if args.action == "set":
            config_data = {}
            if args.app_id:
                config_data["app_id"] = args.app_id
            if args.app_secret:
                config_data["app_secret"] = args.app_secret
            if args.template_id:
                config_data["template_id"] = args.template_id
            if args.preview_openid:
                config_data["preview_openid"] = args.preview_openid
            app.save_wechat_config(config_data)

    elif args.command == "pixivision":
        if args.pixivision_command == "list":
            app.get_pixivision_illustrations(
                args.start_page, args.end_page, args.save, args.query
            )
        elif args.pixivision_command == "detail":
            app.get_pixivision_illustration_detail(args.illustration_id, args.save)
        elif args.pixivision_command == "ranking":
            app.get_pixivision_ranking(args.save)
        elif args.pixivision_command == "recommendations":
            app.get_pixivision_recommendations(args.save)
        elif args.pixivision_command == "save":
            app.store_pixivision_illustration(args.illustration_id)
        elif args.pixivision_command == "get":
            app.get_stored_pixivision_illustration(args.illustration_id)
        elif args.pixivision_command == "stored":
            app.get_stored_pixivision_illustrations(args.limit, args.offset)
        elif args.pixivision_command == "search":
            app.search_pixivision_illustrations(args.keyword, args.limit)
        elif args.pixivision_command == "push":
            app.push_pixivision_illustration()
        elif args.pixivision_command == "download":
            app.download_pixivision_illustration(args.illustration_id, args.output)
        else:
            # 没有提供子命令，打印帮助信息
            pixivision_parser.print_help()
    elif args.command == "schedule":
        if args.schedule_command == "time":
            app.set_schedule_time(args.start, args.end)
        elif args.schedule_command == "frequency":
            app.set_schedule_frequency(args.weekly_frequency)
        elif args.schedule_command == "view":
            app.view_schedule_config()
        elif args.schedule_command == "run":
            app.run_schedule()
        elif args.schedule_command == "run-once":
            app.run_once()
        else:
            # 没有提供子命令，打印帮助信息
            schedule_parser.print_help()
    elif args.command == "draft":
        if args.draft_command == "switch":
            app.draft_switch(args.checkonly)
        elif args.draft_command == "add":
            app.draft_add(
                args.title,
                args.author,
                args.content,
                args.digest,
                args.thumb_media_id,
                args.show_cover_pic,
            )
        elif args.draft_command == "list":
            app.draft_list(args.offset, args.count)
        elif args.draft_command == "count":
            app.draft_count()
        elif args.draft_command == "delete":
            app.draft_delete(args.media_id)
        elif args.draft_command == "get":
            app.draft_get(args.media_id)
        elif args.draft_command == "update":
            app.draft_update(
                args.media_id,
                args.index,
                args.title,
                args.author,
                args.content,
                args.digest,
                args.thumb_media_id,
                args.show_cover_pic,
            )
        elif args.draft_command == "submit":
            app.draft_submit(args.media_id, args.title)
        elif args.draft_command == "create":
            app.draft_create(
                args.source,
                args.title,
                args.author,
                args.compress,
                args.digest,
                args.content,
                args.show_cover,
                args.message_type,
            )
        else:
            # 没有提供子命令，打印帮助信息
            draft_parser.print_help()
    else:
        # 没有提供命令，显示帮助消息
        parser.print_help()


if __name__ == "__main__":
    main()
