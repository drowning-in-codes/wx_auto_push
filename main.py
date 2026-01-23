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
from src.utils.db_manager import DBManager
from src.push.wechat_callback_server import WeChatCallbackServer


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

        # 初始化调度器
        self.schedule_manager = ScheduleManager(self.config, self._run_push_task)

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


if __name__ == "__main__":
    app = WeChatAutoPush()

    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            # 立即执行一次
            app.run_once()
        elif sys.argv[1] == "push":
            # 立即推送指定类型
            content_type = sys.argv[2] if len(sys.argv) > 2 else None
            if content_type and content_type not in ["text", "image"]:
                print("无效的推送类型，请使用: text, image")
            else:
                result = app.push_now(content_type)
                print(f"立即推送任务执行完成，结果: {result}")
        elif sys.argv[1] == "start":
            # 启动调度器
            app.start_schedule()
        elif sys.argv[1] == "stop":
            # 停止调度器
            app.stop_schedule()
        elif sys.argv[1] == "config":
            # 配置微信公众号，包括创建自定义菜单
            print("配置微信公众号...")
            app._initialize_wechat_menu()
            print("微信公众号配置完成")
        elif sys.argv[1] == "material":
            # 素材管理命令
            if len(sys.argv) < 3:
                print("素材管理命令用法:")
                print("  python main.py material count           # 获取素材总数")
                print(
                    "  python main.py material list [type]     # 列出素材，type可选：image, voice, video, thumb"
                )
                print("  python main.py material get <media_id>  # 获取素材")
                print(
                    "  python main.py material upload <type> <file_path> [title] [description]  # 上传素材"
                )
                print("  python main.py material delete <media_id>  # 删除素材")
            else:
                sub_command = sys.argv[2]
                if sub_command == "count":
                    # 获取素材总数
                    app.get_material_count()
                elif sub_command == "list":
                    # 列出素材
                    material_type = sys.argv[3] if len(sys.argv) > 3 else None
                    app.list_materials(material_type)
                elif sub_command == "get":
                    # 获取素材
                    if len(sys.argv) > 3:
                        media_id = sys.argv[3]
                        app.get_material(media_id)
                    else:
                        print("缺少media_id参数")
                elif sub_command == "upload":
                    # 上传素材
                    if len(sys.argv) > 4:
                        material_type = sys.argv[3]
                        file_path = sys.argv[4]
                        title = sys.argv[5] if len(sys.argv) > 5 else None
                        description = sys.argv[6] if len(sys.argv) > 6 else None
                        app.upload_material(
                            material_type, file_path, title, description
                        )
                    else:
                        print("缺少必要参数")
                elif sub_command == "delete":
                    # 删除素材
                    if len(sys.argv) > 3:
                        media_id = sys.argv[3]
                        app.delete_material(media_id)
                    else:
                        print("缺少media_id参数")
                else:
                    print(f"未知的素材管理命令: {sub_command}")
        elif sys.argv[1] == "menu":
            # 菜单管理命令
            if len(sys.argv) < 3:
                print("菜单管理命令用法:")
                print(
                    "  python main.py menu create           # 根据配置文件创建自定义菜单"
                )
                print(
                    "  python main.py menu get              # 获取自定义菜单配置（仅API设置的菜单）"
                )
                print(
                    "  python main.py menu info             # 查询当前自定义菜单信息（包括API和官网设置的菜单）"
                )
                print("  python main.py menu delete           # 删除自定义菜单")
            else:
                sub_command = sys.argv[2]
                if sub_command == "create":
                    # 创建自定义菜单
                    wechat_config = app.config.get_wechat_config()
                    menu_config = wechat_config.get("menu", {})
                    app.push_service.menu_service.create_menu(menu_config)
                elif sub_command == "get":
                    # 获取自定义菜单配置（仅API设置的菜单）
                    result = app.push_service.menu_service.get_menu()
                    print(f"获取自定义菜单配置结果: {result}")
                elif sub_command == "info":
                    # 查询当前自定义菜单信息（包括API和官网设置的菜单）
                    result = app.push_service.menu_service.get_current_selfmenu_info()
                    print(f"查询自定义菜单信息结果: {result}")
                elif sub_command == "delete":
                    # 删除自定义菜单
                    result = app.push_service.menu_service.delete_menu()
                    print(f"删除自定义菜单结果: {result}")
                else:
                    print(f"未知的菜单管理命令: {sub_command}")
        elif sys.argv[1] == "publish":
            # 发布管理命令
            if len(sys.argv) < 3:
                print("发布管理命令用法:")
                print(
                    "  python main.py publish list [offset] [count] [no_content]  # 获取已发布的消息列表"
                )
                print(
                    "  python main.py publish get <article_id>                  # 获取已发布的图文信息"
                )
                print(
                    "  python main.py publish delete <article_id> [index]       # 删除发布文章"
                )
                print(
                    "  python main.py publish status <publish_id>              # 查询发布状态"
                )
                print(
                    "  python main.py publish submit <media_id>                # 发布草稿"
                )
            else:
                sub_command = sys.argv[2]
                if sub_command == "list":
                    # 获取已发布的消息列表
                    offset = int(sys.argv[3]) if len(sys.argv) > 3 else 0
                    count = int(sys.argv[4]) if len(sys.argv) > 4 else 10
                    no_content = int(sys.argv[5]) if len(sys.argv) > 5 else 0
                    app.get_published_news_list(offset, count, no_content)
                elif sub_command == "get":
                    # 获取已发布的图文信息
                    if len(sys.argv) > 3:
                        article_id = sys.argv[3]
                        app.get_published_article(article_id)
                    else:
                        print("缺少article_id参数")
                elif sub_command == "delete":
                    # 删除发布文章
                    if len(sys.argv) > 3:
                        article_id = sys.argv[3]
                        index = int(sys.argv[4]) if len(sys.argv) > 4 else 0
                        app.delete_published_article(article_id, index)
                    else:
                        print("缺少article_id参数")
                elif sub_command == "status":
                    # 查询发布状态
                    if len(sys.argv) > 3:
                        publish_id = sys.argv[3]
                        app.get_publish_status(publish_id)
                    else:
                        print("缺少publish_id参数")
                elif sub_command == "submit":
                    # 发布草稿
                    if len(sys.argv) > 3:
                        media_id = sys.argv[3]
                        app.submit_publish(media_id)
                    else:
                        print("缺少media_id参数")
                else:
                    print(f"未知的发布管理命令: {sub_command}")
        else:
            print(
                "未知命令，请使用: run, push [text|image], start, stop, config, material, menu, publish"
            )
    else:
        # 默认启动调度器
        print("启动微信公众号自动推送程序...")
        app.start_schedule()
