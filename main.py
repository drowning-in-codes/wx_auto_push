import random
import sys
import os
from datetime import datetime
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.crawlers.crawler_factory import CrawlerFactory
from src.utils.llm_client import LLMClient
from src.push.wechat_push_service import WeChatPushService
from src.scheduler.schedule_manager import ScheduleManager
from src.utils.db_manager import DBManager
from src.push.wechat_callback_server import WeChatCallbackServer
from src.push.pixivision_service import PixivisionService


class WeChatAutoPush:
    def __init__(self):
        self.config = Config()
        self.anime_crawler = None
        self.image_crawler = None
        self.llm_client = None
        self.push_service = None
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

        # 初始化 Pixivision 服务
        proxy_config = self.config.get_proxy_config()
        self.pixivision_service = PixivisionService(proxy_config)

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
            "token": "WECHAT_TOKEN",
            "preview_enabled": "WECHAT_PREVIEW_ENABLED",
            "preview_towxname": "WECHAT_PREVIEW_TOWXNAME",
        }

        # 更新配置
        updated_lines = []
        for line in existing_lines:
            line = line.strip()
            # 检查是否是我们要更新的配置项
            updated = False
            for key, env_var in config_map.items():
                if line.startswith(f"{env_var}="):
                    if key in config_data:
                        if key == "preview_enabled":
                            value = "true" if config_data[key] else "false"
                        else:
                            value = config_data[key]
                        updated_lines.append(f"{env_var}={value}\n")
                        updated = True
                    break
            if not updated:
                updated_lines.append(line + "\n")

        # 添加新的配置项
        for key, env_var in config_map.items():
            if key in config_data:
                # 检查是否已经存在
                exists = False
                for line in updated_lines:
                    if line.startswith(f"{env_var}="):
                        exists = True
                        break
                if not exists:
                    if key == "preview_enabled":
                        value = "true" if config_data[key] else "false"
                    else:
                        value = config_data[key]
                    updated_lines.append(f"{env_var}={value}\n")

        # 写入 .env 文件
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        print(f"配置已保存到 {env_file} 文件")

    def login(self):
        """
        登录微信公众号，获取并存储 token
        """
        print("正在登录微信公众号...")

        try:
            # 尝试获取 access token
            access_token = self.push_service.client.get_access_token()

            # 检查 token 是否有效
            if access_token:
                print("登录成功！")
                print(f"Access Token: {access_token[:20]}...")  # 只显示前20个字符
                print("Token 已存储到缓存中")

                # 获取 token 过期时间
                from datetime import datetime

                expire_time = self.push_service.client.token_expire_time
                expire_datetime = datetime.fromtimestamp(expire_time)
                print(f"Token 过期时间: {expire_datetime}")
            else:
                print("登录失败：无法获取 access token")
        except Exception as e:
            print(f"登录失败: {e}")

    def _initialize_callback_server(self):
        """
        初始化并启动微信回调服务器
        """
        callback_config = self.config.get_wechat_config().get("callback", {})
        if callback_config.get("enabled", False):
            self.callback_server = WeChatCallbackServer(
                self.config, self.db_manager, self.push_service
            )
            # 启动回调服务器
            self.callback_server.run()

    def _initialize_wechat_menu(self):
        """
        初始化微信自定义菜单
        """
        print("初始化微信自定义菜单...")
        wechat_config = self.config.get_wechat_config()
        menu_config = wechat_config.get("menu", {})
        self.push_service.menu_service.create_menu(menu_config)
        print("微信自定义菜单初始化完成")

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

                # 插入消息记录（待发送）
                message_id = self.db_manager.insert_message(
                    task_id=clientmsgid,
                    title=news["title"],
                    content=news.get("content", news["title"]),
                    status=0,
                )

                try:
                    # 检查是否需要预览
                    preview_config = self.config.get_wechat_config().get("preview", {})
                    if preview_config.get("enabled"):
                        print("发送预览消息...")
                        # 发送预览消息
                        preview_result = self.push_service.preview_news_message(
                            news["title"],
                            news.get("content", news["title"]),
                            "",  # 可以添加默认图片
                            news["url"],
                        )
                        print(f"预览消息发送结果: {preview_result}")
                        print("预览消息已发送，请在手机上查看效果")

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

                    # 获取msg_id并更新到数据库
                    msg_id = result.get("msg_id")
                    if msg_id:
                        self.db_manager.update_message_msg_id(
                            message_id=message_id, msg_id=msg_id
                        )
                        # 设置35分钟后检查消息状态
                        self._schedule_status_check(
                            message_id=message_id, msg_id=msg_id
                        )

                    # 更新消息状态为已发送
                    self.db_manager.update_message_status(
                        message_id=message_id, status=1, send_time=datetime.now()
                    )
                except Exception as e:
                    print(f"推送失败: {e}")
                    # 更新消息状态为失败
                    self.db_manager.update_message_status(
                        message_id=message_id, status=2
                    )
            else:
                print("未爬取到新闻内容")
                # 插入爬取失败的记录
                self.db_manager.insert_message(
                    task_id=clientmsgid,
                    title="爬取失败 - 动漫新闻",
                    content="未能爬取到动漫新闻内容",
                    status=2,
                )

        elif content_type == "image":
            # 爬取图片
            image = self.image_crawler.crawl() if self.image_crawler else None

            if image:
                # 插入消息记录（待发送）
                message_id = self.db_manager.insert_message(
                    task_id=clientmsgid,
                    title=image.get("alt", "动漫图片"),
                    content=image.get("alt", "动漫图片"),
                    status=0,
                )

                try:
                    # 获取图片发布方式配置
                    push_config = self.config.get_push_config()
                    image_publish_type = push_config.get("image_publish_type", "image")

                    # 检查是否需要预览
                    preview_config = self.config.get_wechat_config().get("preview", {})
                    if preview_config.get("enabled"):
                        print("发送预览消息...")
                        # 根据配置发送不同类型的预览消息
                        if image_publish_type == "news":
                            # 发送图文预览消息
                            preview_result = self.push_service.preview_news_message(
                                image.get("alt", "图片分享"),
                                image.get("alt", "分享一张图片"),
                                image["url"],
                                image.get("url", ""),
                            )
                        else:
                            # 发送图片预览消息
                            preview_result = self.push_service.preview_image_message(
                                image["url"], image.get("alt", "动漫图片")
                            )
                        print(f"预览消息发送结果: {preview_result}")
                        print("预览消息已发送，请在手机上查看效果")

                    # 根据配置推送不同类型的消息
                    if image_publish_type == "news":
                        # 推送为图文消息
                        result = self.push_service.push_news_article(
                            image.get("alt", "图片分享"),
                            image.get("alt", "分享一张图片"),
                            image["url"],
                            image.get("url", ""),
                            clientmsgid=clientmsgid,
                            send_ignore=False,
                        )
                    else:
                        # 推送为图片消息
                        result = self.push_service.push_image_content(
                            image["url"],
                            image.get("alt", "动漫图片"),
                            clientmsgid=clientmsgid,
                        )
                    print(f"推送图片结果: {result}")

                    # 获取msg_id并更新到数据库
                    msg_id = result.get("msg_id")
                    if msg_id:
                        self.db_manager.update_message_msg_id(
                            message_id=message_id, msg_id=msg_id
                        )
                        # 设置35分钟后检查消息状态
                        self._schedule_status_check(
                            message_id=message_id, msg_id=msg_id
                        )

                    # 更新消息状态为已发送
                    self.db_manager.update_message_status(
                        message_id=message_id, status=1, send_time=datetime.now()
                    )
                except Exception as e:
                    print(f"推送失败: {e}")
                    # 更新消息状态为失败
                    self.db_manager.update_message_status(
                        message_id=message_id, status=2
                    )
            else:
                print("未爬取到图片内容")
                # 插入爬取失败的记录
                self.db_manager.insert_message(
                    task_id=clientmsgid,
                    title="爬取失败 - 动漫图片",
                    content="未能爬取到动漫图片内容",
                    status=2,
                )

        print("推送任务执行完成")

    def run_once(self):
        """立即执行一次推送任务"""
        return self.schedule_manager.run_once()

    def push_now(self, content_type=None):
        """
        立即推送指定类型的内容
        :param content_type: 推送类型，可选值："text", "image"，默认随机
        :return: 推送结果
        """
        print("开始执行立即推送任务...")

        # 如果未指定类型，随机选择
        if not content_type:
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

                # 插入消息记录（待发送）
                message_id = self.db_manager.insert_message(
                    task_id=clientmsgid,
                    title=news["title"],
                    content=news.get("content", news["title"]),
                    status=0,
                )

                try:
                    # 检查是否需要预览
                    preview_config = self.config.get_wechat_config().get("preview", {})
                    if preview_config.get("enabled"):
                        print("发送预览消息...")
                        # 发送预览消息
                        preview_result = self.push_service.preview_news_message(
                            news["title"],
                            news.get("content", news["title"]),
                            "",  # 可以添加默认图片
                            news["url"],
                        )
                        print(f"预览消息发送结果: {preview_result}")
                        print("预览消息已发送，请在手机上查看效果")

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

                    # 获取msg_id并更新到数据库
                    msg_id = result.get("msg_id")
                    if msg_id:
                        self.db_manager.update_message_msg_id(
                            message_id=message_id, msg_id=msg_id
                        )
                        # 设置35分钟后检查消息状态
                        self._schedule_status_check(
                            message_id=message_id, msg_id=msg_id
                        )

                    # 更新消息状态为已发送
                    self.db_manager.update_message_status(
                        message_id=message_id, status=1, send_time=datetime.now()
                    )
                    return result
                except Exception as e:
                    print(f"推送失败: {e}")
                    # 更新消息状态为失败
                    self.db_manager.update_message_status(
                        message_id=message_id, status=2
                    )
                    return None
            else:
                print("未爬取到新闻内容")
                return None

        elif content_type == "image":
            # 爬取图片
            image = self.image_crawler.crawl() if self.image_crawler else None

            if image:
                # 插入消息记录（待发送）
                message_id = self.db_manager.insert_message(
                    task_id=clientmsgid,
                    title=image.get("alt", "动漫图片"),
                    content=image.get("alt", "动漫图片"),
                    status=0,
                )

                try:
                    # 获取图片发布方式配置
                    push_config = self.config.get_push_config()
                    image_publish_type = push_config.get("image_publish_type", "image")

                    # 检查是否需要预览
                    preview_config = self.config.get_wechat_config().get("preview", {})
                    if preview_config.get("enabled"):
                        print("发送预览消息...")
                        # 根据配置发送不同类型的预览消息
                        if image_publish_type == "news":
                            # 发送图文预览消息
                            preview_result = self.push_service.preview_news_message(
                                image.get("alt", "图片分享"),
                                image.get("alt", "分享一张图片"),
                                image["url"],
                                image.get("url", ""),
                            )
                        else:
                            # 发送图片预览消息
                            preview_result = self.push_service.preview_image_message(
                                image["url"], image.get("alt", "动漫图片")
                            )
                        print(f"预览消息发送结果: {preview_result}")
                        print("预览消息已发送，请在手机上查看效果")

                    # 根据配置推送不同类型的消息
                    if image_publish_type == "news":
                        # 推送为图文消息
                        result = self.push_service.push_news_article(
                            image.get("alt", "图片分享"),
                            image.get("alt", "分享一张图片"),
                            image["url"],
                            image.get("url", ""),
                            clientmsgid=clientmsgid,
                            send_ignore=False,
                        )
                    else:
                        # 推送为图片消息
                        result = self.push_service.push_image_content(
                            image["url"],
                            image.get("alt", "动漫图片"),
                            clientmsgid=clientmsgid,
                        )
                    print(f"推送图片结果: {result}")

                    # 获取msg_id并更新到数据库
                    msg_id = result.get("msg_id")
                    if msg_id:
                        self.db_manager.update_message_msg_id(
                            message_id=message_id, msg_id=msg_id
                        )
                        # 设置35分钟后检查消息状态
                        self._schedule_status_check(
                            message_id=message_id, msg_id=msg_id
                        )

                    # 更新消息状态为已发送
                    self.db_manager.update_message_status(
                        message_id=message_id, status=1, send_time=datetime.now()
                    )
                    return result
                except Exception as e:
                    print(f"推送失败: {e}")
                    # 更新消息状态为失败
                    self.db_manager.update_message_status(
                        message_id=message_id, status=2
                    )
                    return None
            else:
                print("未爬取到图片内容")
                return None

        print("立即推送任务执行完成")

    def start_schedule(self):
        """启动调度器，开始定时执行任务"""
        self.schedule_manager.start()

    def _schedule_status_check(self, message_id, msg_id):
        """
        设置定时检查消息状态的任务
        """
        # 35分钟后检查状态
        from datetime import datetime, timedelta

        run_time = datetime.now() + timedelta(minutes=35)

        # 使用APScheduler添加定时任务
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=self.check_message_status,
            args=[message_id, msg_id],
            trigger="date",
            run_date=run_time,
            id=f"check_status_{message_id}_{msg_id}",
            replace_existing=True,
        )
        scheduler.start()
        print(f"已设置35分钟后检查消息状态的任务: {message_id}, {msg_id}")

    def check_message_status(self, message_id, msg_id):
        """
        检查消息发送状态
        """
        try:
            # 获取消息状态
            status_result = self.push_service.wechat_client.get_mass_status(msg_id)
            print(f"检查消息状态结果: {status_result}")

            # 根据状态更新数据库
            msg_status = status_result.get("msg_status")
            if msg_status == "SEND_SUCCESS":
                # 发送成功
                self.db_manager.update_message_status(
                    message_id=message_id, status=1, send_time=datetime.now()
                )
                print(f"消息 {msg_id} 发送成功")
            elif msg_status == "SEND_FAIL":
                # 发送失败
                self.db_manager.update_message_status(message_id=message_id, status=2)
                print(f"消息 {msg_id} 发送失败")
            elif msg_status in ["SENDING", "DELETE"]:
                # 发送中或已删除，不更新状态
                print(f"消息 {msg_id} 状态: {msg_status}")
        except Exception as e:
            print(f"检查消息状态失败: {e}")

    # 素材管理相关方法
    def get_material_count(self):
        """
        获取素材总数
        """
        try:
            result = self.push_service.material_service.get_material_count()
            print(f"获取素材总数结果: {result}")
        except Exception as e:
            print(f"获取素材总数失败: {e}")

    def list_materials(self, material_type=None):
        """
        列出素材
        """
        print(f"暂未实现列出素材功能，material_type: {material_type}")

    def get_material(self, media_id):
        """
        获取素材
        """
        try:
            result = self.push_service.material_service.get_material(media_id)
            print(f"获取素材结果: {result}")
        except Exception as e:
            print(f"获取素材失败: {e}")

    def upload_material(self, material_type, file_path, title=None, description=None):
        """
        上传素材
        """
        try:
            result = self.push_service.material_service.add_material(
                material_type, file_path, title, description
            )
            print(f"上传素材结果: {result}")
        except Exception as e:
            print(f"上传素材失败: {e}")

    def delete_material(self, media_id):
        """
        删除素材
        """
        try:
            result = self.push_service.material_service.delete_material(media_id)
            print(f"删除素材结果: {result}")
        except Exception as e:
            print(f"删除素材失败: {e}")

    # 发布相关方法
    def get_published_news_list(self, offset=0, count=10, no_content=0):
        """
        获取已发布的消息列表
        """
        try:
            result = self.push_service.publish_service.get_published_news_list(
                offset, count, no_content
            )
            print(f"获取已发布消息列表结果: {result}")
        except Exception as e:
            print(f"获取已发布消息列表失败: {e}")

    def get_published_article(self, article_id):
        """
        获取已发布的图文信息
        """
        try:
            result = self.push_service.publish_service.get_published_article(article_id)
            print(f"获取已发布图文信息结果: {result}")
        except Exception as e:
            print(f"获取已发布图文信息失败: {e}")

    def delete_published_article(self, article_id, index=0):
        """
        删除发布文章
        """
        try:
            result = self.push_service.publish_service.delete_published_article(
                article_id, index
            )
            print(f"删除发布文章结果: {result}")
        except Exception as e:
            print(f"删除发布文章失败: {e}")

    def get_publish_status(self, publish_id):
        """
        发布状态查询
        """
        try:
            result = self.push_service.publish_service.get_publish_status(publish_id)
            print(f"查询发布状态结果: {result}")
        except Exception as e:
            print(f"查询发布状态失败: {e}")

    def submit_publish(self, media_id):
        """
        发布草稿
        """
        try:
            result = self.push_service.publish_service.submit_publish(media_id)
            print(f"发布草稿结果: {result}")
        except Exception as e:
            print(f"发布草稿失败: {e}")

    # Pixivision 相关方法
    def get_pixivision_illustrations(self, start_page=1, end_page=1):
        """
        获取 Pixivision 插画列表
        """
        try:
            illustrations = self.pixivision_service.get_illustration_list(
                start_page, end_page
            )
            print(f"获取到 {len(illustrations)} 个插画")
            for i, illustration in enumerate(illustrations, 1):
                print(f"{i}. {illustration['title']}")
                print(f"   URL: {illustration['url']}")
                print(f"   图片: {illustration['image_url']}")
                print(f"   标签: {', '.join(illustration['tags'])}")
                print()
            return illustrations
        except Exception as e:
            print(f"获取 Pixivision 插画失败: {e}")
            return []

    def get_pixivision_illustration_detail(self, illustration_id):
        """
        获取 Pixivision 插画详情
        """
        try:
            detail = self.pixivision_service.get_illustration_by_id(illustration_id)
            if detail:
                print(f"标题: {detail['title']}")
                print(f"URL: {detail['url']}")
                print(f"内容: {detail['content']}")
                print(f"图片数量: {len(detail['images'])}")
                for i, image_url in enumerate(detail["images"], 1):
                    print(f"图片 {i}: {image_url}")
                print(f"标签: {', '.join(detail['tags'])}")
            return detail
        except Exception as e:
            print(f"获取 Pixivision 插画详情失败: {e}")
            return None

    def push_pixivision_illustration(self, illustration_id):
        """
        推送 Pixivision 插画
        """
        try:
            # 获取插画详情
            detail = self.pixivision_service.get_illustration_by_id(illustration_id)
            if not detail:
                print("获取插画详情失败")
                return None

            # 生成clientmsgid以避免重复推送
            import uuid

            clientmsgid = str(uuid.uuid4())

            # 插入消息记录（待发送）
            message_id = self.db_manager.insert_message(
                task_id=clientmsgid,
                title=detail["title"],
                content=detail["content"],
                status=0,
            )

            # 推送为图文消息
            if detail["images"]:
                result = self.push_service.push_news_article(
                    detail["title"],
                    detail["content"],
                    detail["images"][0],  # 使用第一张图片
                    detail["url"],
                    clientmsgid=clientmsgid,
                    send_ignore=False,
                )
                print(f"推送 Pixivision 插画结果: {result}")

                # 获取msg_id并更新到数据库
                msg_id = result.get("msg_id")
                if msg_id:
                    self.db_manager.update_message_msg_id(
                        message_id=message_id, msg_id=msg_id
                    )
                    # 设置35分钟后检查消息状态
                    self._schedule_status_check(message_id=message_id, msg_id=msg_id)

                # 更新消息状态为已发送
                self.db_manager.update_message_status(
                    message_id=message_id, status=1, send_time=datetime.now()
                )
                return result
            else:
                print("插画没有图片")
                return None
        except Exception as e:
            print(f"推送 Pixivision 插画失败: {e}")
            return None


def main():
    app = WeChatAutoPush()

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        prog="wx-auto-push",
        description="微信公众号自动推送程序，支持定时推送动漫新闻和图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  # 立即执行一次推送任务
  python main.py run

  # 立即推送指定类型的内容
  python main.py push text
  python main.py push image

  # 启动调度器
  python main.py start

  # 管理素材
  python main.py material count
  python main.py material list image
  python main.py material get <media_id>
  python main.py material upload image path/to/image.jpg
  python main.py material delete <media_id>

  # 管理菜单
  python main.py menu create
  python main.py menu get
  python main.py menu info
  python main.py menu delete

  # 管理发布
  python main.py publish list
  python main.py publish get <article_id>
  python main.py publish delete <article_id>
  python main.py publish status <publish_id>
  python main.py publish submit <media_id>

  # 管理 Pixivision 插画
  python main.py pixivision list 1 2
  python main.py pixivision get 11525
  python main.py pixivision push 11525
""",
    )

    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # run 命令
    run_parser = subparsers.add_parser("run", help="立即执行一次推送任务")

    # push 命令
    push_parser = subparsers.add_parser("push", help="立即推送指定类型的内容")
    push_parser.add_argument(
        "content_type",
        nargs="?",
        choices=["text", "image"],
        help="推送类型: text, image",
    )

    # start 命令
    start_parser = subparsers.add_parser("start", help="启动调度器")

    # stop 命令
    stop_parser = subparsers.add_parser("stop", help="停止调度器")

    # login 命令
    login_parser = subparsers.add_parser(
        "login", help="使用 appid 和 app secret 获取并存储 token"
    )

    # config 命令
    config_parser = subparsers.add_parser(
        "config", help="配置微信公众号，包括创建自定义菜单"
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_command", help="配置子命令"
    )

    # config menu 命令
    config_subparsers.add_parser("menu", help="根据配置文件创建自定义菜单")

    # config set 命令
    config_set_parser = config_subparsers.add_parser("set", help="设置微信公众号配置")
    config_set_parser.add_argument("--app-id", help="微信公众号 App ID")
    config_set_parser.add_argument("--app-secret", help="微信公众号 App Secret")
    config_set_parser.add_argument("--template-id", help="微信公众号模板消息 ID")
    config_set_parser.add_argument("--token", help="微信公众号 Token")
    config_set_parser.add_argument(
        "--preview-enabled", type=bool, help="是否启用预览功能"
    )
    config_set_parser.add_argument("--preview-towxname", help="预览接收者微信号")

    # material 命令
    material_parser = subparsers.add_parser("material", help="素材管理命令")
    material_subparsers = material_parser.add_subparsers(
        dest="material_command", help="素材管理子命令"
    )

    # material count 命令
    material_subparsers.add_parser("count", help="获取素材总数")

    # material list 命令
    material_list_parser = material_subparsers.add_parser("list", help="列出素材")
    material_list_parser.add_argument(
        "type", nargs="?", help="素材类型: image, voice, video, thumb"
    )

    # material get 命令
    material_get_parser = material_subparsers.add_parser("get", help="获取素材")
    material_get_parser.add_argument("media_id", help="素材ID")

    # material upload 命令
    material_upload_parser = material_subparsers.add_parser("upload", help="上传素材")
    material_upload_parser.add_argument(
        "type", help="素材类型: image, voice, video, thumb"
    )
    material_upload_parser.add_argument("file_path", help="文件路径")
    material_upload_parser.add_argument("title", nargs="?", help="素材标题")
    material_upload_parser.add_argument("description", nargs="?", help="素材描述")

    # material delete 命令
    material_delete_parser = material_subparsers.add_parser("delete", help="删除素材")
    material_delete_parser.add_argument("media_id", help="素材ID")

    # menu 命令
    menu_parser = subparsers.add_parser("menu", help="菜单管理命令")
    menu_subparsers = menu_parser.add_subparsers(
        dest="menu_command", help="菜单管理子命令"
    )

    # menu create 命令
    menu_subparsers.add_parser("create", help="根据配置文件创建自定义菜单")

    # menu get 命令
    menu_subparsers.add_parser("get", help="获取自定义菜单配置（仅API设置的菜单）")

    # menu info 命令
    menu_subparsers.add_parser(
        "info", help="查询当前自定义菜单信息（包括API和官网设置的菜单）"
    )

    # menu delete 命令
    menu_subparsers.add_parser("delete", help="删除自定义菜单")

    # publish 命令
    publish_parser = subparsers.add_parser("publish", help="发布管理命令")
    publish_subparsers = publish_parser.add_subparsers(
        dest="publish_command", help="发布管理子命令"
    )

    # publish list 命令
    publish_list_parser = publish_subparsers.add_parser(
        "list", help="获取已发布的消息列表"
    )
    publish_list_parser.add_argument(
        "offset", nargs="?", type=int, default=0, help="偏移量"
    )
    publish_list_parser.add_argument(
        "count", nargs="?", type=int, default=10, help="数量"
    )
    publish_list_parser.add_argument(
        "no_content", nargs="?", type=int, default=0, help="是否返回内容"
    )

    # publish get 命令
    publish_get_parser = publish_subparsers.add_parser(
        "get", help="获取已发布的图文信息"
    )
    publish_get_parser.add_argument("article_id", help="文章ID")

    # publish delete 命令
    publish_delete_parser = publish_subparsers.add_parser("delete", help="删除发布文章")
    publish_delete_parser.add_argument("article_id", help="文章ID")
    publish_delete_parser.add_argument(
        "index", nargs="?", type=int, default=0, help="文章索引"
    )

    # publish status 命令
    publish_status_parser = publish_subparsers.add_parser("status", help="查询发布状态")
    publish_status_parser.add_argument("publish_id", help="发布ID")

    # publish submit 命令
    publish_submit_parser = publish_subparsers.add_parser("submit", help="发布草稿")
    publish_submit_parser.add_argument("media_id", help="素材ID")

    # pixivision 命令
    pixivision_parser = subparsers.add_parser("pixivision", help="Pixivision 管理命令")
    pixivision_subparsers = pixivision_parser.add_subparsers(
        dest="pixivision_command", help="Pixivision 管理子命令"
    )

    # pixivision list 命令
    pixivision_list_parser = pixivision_subparsers.add_parser(
        "list", help="获取插画列表"
    )
    pixivision_list_parser.add_argument(
        "start_page", nargs="?", type=int, default=1, help="开始页码"
    )
    pixivision_list_parser.add_argument(
        "end_page", nargs="?", type=int, help="结束页码"
    )

    # pixivision get 命令
    pixivision_get_parser = pixivision_subparsers.add_parser("get", help="获取插画详情")
    pixivision_get_parser.add_argument("illustration_id", help="插画ID")

    # pixivision push 命令
    pixivision_push_parser = pixivision_subparsers.add_parser(
        "push", help="推送插画到微信"
    )
    pixivision_push_parser.add_argument("illustration_id", help="插画ID")

    # 解析命令行参数
    args = parser.parse_args()

    # 处理命令
    if args.command == "run":
        # 立即执行一次
        app.run_once()
    elif args.command == "push":
        # 立即推送指定类型
        content_type = args.content_type
        if content_type and content_type not in ["text", "image"]:
            print("无效的推送类型，请使用: text, image")
        else:
            result = app.push_now(content_type)
            print(f"立即推送任务执行完成，结果: {result}")
    elif args.command == "start":
        # 启动调度器
        app.start_schedule()
    elif args.command == "stop":
        # 停止调度器
        app.stop_schedule()
    elif args.command == "login":
        # 登录微信公众号，获取并存储 token
        app.login()
    elif args.command == "config":
        # 配置微信公众号
        if args.config_command == "menu":
            # 创建自定义菜单
            print("配置微信公众号...")
            app._initialize_wechat_menu()
            print("微信公众号配置完成")
        elif args.config_command == "set":
            # 设置微信公众号配置
            print("设置微信公众号配置...")
            config_data = {}
            if args.app_id:
                config_data["app_id"] = args.app_id
                print(f"App ID: {args.app_id}")
            if args.app_secret:
                config_data["app_secret"] = args.app_secret
                print("App Secret: ******")
            if args.template_id:
                config_data["template_id"] = args.template_id
                print(f"Template ID: {args.template_id}")
            if args.token:
                config_data["token"] = args.token
                print(f"Token: {args.token}")
            if args.preview_enabled is not None:
                config_data["preview_enabled"] = args.preview_enabled
                print(f"Preview Enabled: {args.preview_enabled}")
            if args.preview_towxname:
                config_data["preview_towxname"] = args.preview_towxname
                print(f"Preview ToWxName: {args.preview_towxname}")

            if config_data:
                # 保存配置到 .env 文件
                app.save_wechat_config(config_data)
                print("配置设置成功！")
            else:
                print("没有设置任何配置")
        else:
            config_parser.print_help()
    elif args.command == "material":
        # 素材管理命令
        if args.material_command == "count":
            # 获取素材总数
            app.get_material_count()
        elif args.material_command == "list":
            # 列出素材
            material_type = args.type
            app.list_materials(material_type)
        elif args.material_command == "get":
            # 获取素材
            media_id = args.media_id
            app.get_material(media_id)
        elif args.material_command == "upload":
            # 上传素材
            material_type = args.type
            file_path = args.file_path
            title = args.title
            description = args.description
            app.upload_material(material_type, file_path, title, description)
        elif args.material_command == "delete":
            # 删除素材
            media_id = args.media_id
            app.delete_material(media_id)
        else:
            material_parser.print_help()
    elif args.command == "menu":
        # 菜单管理命令
        if args.menu_command == "create":
            # 创建自定义菜单
            wechat_config = app.config.get_wechat_config()
            menu_config = wechat_config.get("menu", {})
            app.push_service.menu_service.create_menu(menu_config)
        elif args.menu_command == "get":
            # 获取自定义菜单配置（仅API设置的菜单）
            result = app.push_service.menu_service.get_menu()
            print(f"获取自定义菜单配置结果: {result}")
        elif args.menu_command == "info":
            # 查询当前自定义菜单信息（包括API和官网设置的菜单）
            result = app.push_service.menu_service.get_current_selfmenu_info()
            print(f"查询自定义菜单信息结果: {result}")
        elif args.menu_command == "delete":
            # 删除自定义菜单
            result = app.push_service.menu_service.delete_menu()
            print(f"删除自定义菜单结果: {result}")
        else:
            menu_parser.print_help()
    elif args.command == "publish":
        # 发布管理命令
        if args.publish_command == "list":
            # 获取已发布的消息列表
            offset = args.offset
            count = args.count
            no_content = args.no_content
            app.get_published_news_list(offset, count, no_content)
        elif args.publish_command == "get":
            # 获取已发布的图文信息
            article_id = args.article_id
            app.get_published_article(article_id)
        elif args.publish_command == "delete":
            # 删除发布文章
            article_id = args.article_id
            index = args.index
            app.delete_published_article(article_id, index)
        elif args.publish_command == "status":
            # 查询发布状态
            publish_id = args.publish_id
            app.get_publish_status(publish_id)
        elif args.publish_command == "submit":
            # 发布草稿
            media_id = args.media_id
            app.submit_publish(media_id)
        else:
            publish_parser.print_help()
    elif args.command == "pixivision":
        # Pixivision 管理命令
        if args.pixivision_command == "list":
            # 获取插画列表
            start_page = args.start_page
            end_page = args.end_page if args.end_page else start_page
            app.get_pixivision_illustrations(start_page, end_page)
        elif args.pixivision_command == "get":
            # 获取插画详情
            illustration_id = args.illustration_id
            app.get_pixivision_illustration_detail(illustration_id)
        elif args.pixivision_command == "push":
            # 推送插画
            illustration_id = args.illustration_id
            app.push_pixivision_illustration(illustration_id)
        else:
            pixivision_parser.print_help()
    else:
        # 没有指定命令，显示帮助信息
        parser.print_help()


if __name__ == "__main__":
    main()
