import os
import tempfile
import time
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.image_compressor import ImageCompressor
from src.push.upload_history_service import UploadHistoryService
from src.utils.proxy_pool_service import ProxyPoolService

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DownloadAndDraftService:
    def __init__(self, push_service, draft_service, pixivision_service, config):
        """
        初始化草稿服务
        :param push_service: WeChatPushService 实例
        :param draft_service: WeChatDraftService 实例
        :param pixivision_service: PixivisionService 实例
        :param config: Config 实例
        """
        self.push_service = push_service
        self.draft_service = draft_service
        self.pixivision_service = pixivision_service
        self.config = config
        self.proxy_config = config.get_proxy_config()
        self.proxy_pool_config = config.get_proxy_pool_config()
        self.request_config = config.get_request_config()
        self.download_config = config.get_download_config()
        self.upload_history = UploadHistoryService()

        # 初始化代理池服务
        self.proxy_pool = None
        enable_crawl_proxy_pool = self.download_config.get("enable_crawl_proxy_pool", False)
        if enable_crawl_proxy_pool and self.proxy_pool_config.get("enabled"):
            self.proxy_pool = ProxyPoolService(self.proxy_pool_config)

    def _get_pixiv_headers(self):
        return {
            "Referer": "https://www.pixiv.net/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def _download_single_image(self, image_url, index, total, max_retries=3):
        """
        下载单张图片，支持重试

        :param image_url: 图片URL
        :param index: 图片索引
        :param total: 图片总数
        :param max_retries: 最大重试次数
        :return: (success, temp_image_path) 成功状态和临时文件路径
        """
        for attempt in range(max_retries):
            try:
                # 添加请求延迟（第一次不延迟）
                if index > 0 and self.request_config:
                    delay = self.request_config.get("delay", 1)
                    if delay > 0:
                        time.sleep(delay)

                logger.info(
                    f"下载图片 {index+1}/{total}: {image_url} (尝试 {attempt+1}/{max_retries})"
                )

                # 配置代理
                proxy_config = None
                # 优先使用代理池
                if self.proxy_pool:
                    proxy_config = self.proxy_pool.get_proxy()
                # 如果代理池未启用或未获取到代理，使用传统代理配置
                elif self.proxy_config and self.proxy_config.get("enabled", False):
                    http_proxy = self.proxy_config.get("http_proxy", "")
                    https_proxy = self.proxy_config.get("https_proxy", "")
                    if http_proxy or https_proxy:
                        proxy_config = {
                            "http": http_proxy,
                            "https": https_proxy,
                        }
                else:
                    # 显式禁用代理，覆盖系统环境中的代理配置
                    os.environ["HTTP_PROXY"] = ""
                    os.environ["HTTPS_PROXY"] = ""

                # 创建临时文件
                with tempfile.NamedTemporaryFile(
                    suffix=".jpg", delete=False
                ) as temp_file:
                    temp_image_path = temp_file.name

                headers = self._get_pixiv_headers()
                response = requests.get(
                    image_url, timeout=10, proxies=proxy_config, headers=headers
                )
                response.raise_for_status()

                # 保存图片
                with open(temp_image_path, "wb") as f:
                    f.write(response.content)

                logger.info(f"图片 {index+1}/{total} 下载成功")
                return True, temp_image_path

            except Exception as e:
                logger.error(
                    f"图片 {index+1}/{total} 下载失败 (尝试 {attempt+1}/{max_retries}): {e}"
                )
                # 如果还有重试机会，等待后重试
                if attempt < max_retries - 1:
                    retry_delay = 2**attempt  # 指数退避
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"图片 {index+1}/{total} 超过最大重试次数，跳过")
                    return False, None

        return False, None

    def create_draft(
        self,
        source,
        title=None,
        author=None,
        compress=None,
        digest=None,
        content=None,
        show_cover=1,
        message_type="newspic",  # news: 图文消息, newspic: 图片消息
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
        try:
            # 获取配置
            draft_config = self.config.get_draft_config()
            compression_config = self.config.get_image_compression_config()

            # 使用配置默认值
            if author is None:
                author = draft_config.get("default_author", "公众号作者")

            # 裁剪作者长度不超过16个字符
            if author and len(author) > 16:
                author = author[:16]
                print(f"作者超过16个字符，已裁剪为: {author}")

            if show_cover is None:
                show_cover = draft_config.get("default_show_cover", 1)

            # 裁剪标题长度不超过32个字符
            if title and len(title) > 32:
                title = title[:32]
                print(f"标题超过32个字符，已裁剪为: {title}")

            # 检查消息类型
            is_image_message = message_type == "newspic"

            # 处理压缩参数
            if compress is None:
                compress = compression_config.get("enabled", True)

            # 创建压缩器
            compressor = ImageCompressor(
                max_size=compression_config.get("max_size", 1048576),
                max_dimension=compression_config.get("max_dimension", 2000),
                quality=compression_config.get("quality", 85),
            )

            image_files = []
            temp_files = []

            # 判断图片来源
            if source.isdigit():
                # Pixivision 文章ID
                illustration_id = source
                print(f"从 Pixivision 获取插画 {illustration_id} 的图片...")
                detail = self.pixivision_service.get_illustration_by_id(illustration_id)
                if not detail or not detail.get("images"):
                    print("获取插画详情失败或没有图片")
                    return None

                # 自动生成标题（默认为空）
                if title is None:
                    title = ""

                # 如果标题为空，从Pixivision页面中提取标题
                if not title and detail.get("title"):
                    title = detail.get("title")
                    print(f"从Pixivision页面提取标题: {title}")

                # 裁剪标题长度不超过32个字符
                if title and len(title) > 32:
                    title = title[:32]
                    print(f"标题超过32个字符，已裁剪为: {title}")

                # 下载图片
                images = detail["images"]
                print(f"找到 {len(images)} 张图片")
                logger.info(f"开始多线程下载 {len(images)} 张图片")

                # 使用多线程下载图片
                max_workers = min(
                    self.download_config.get("max_workers", 5), len(images)
                )
                max_retries = self.download_config.get("max_retries", 3)
                logger.info(f"线程数: {max_workers}, 最大重试次数: {max_retries}")

                executor = ThreadPoolExecutor(max_workers=max_workers)
                future_to_index = {
                    executor.submit(
                        self._download_single_image,
                        image_url,
                        i,
                        len(images),
                        max_retries,
                    ): i
                    for i, image_url in enumerate(images)
                }

                try:
                    # 处理下载结果
                    for future in as_completed(future_to_index):
                        index = future_to_index[future]
                        try:
                            success, temp_image_path = future.result()
                            if success and temp_image_path:
                                image_files.append(temp_image_path)
                                temp_files.append(temp_image_path)
                            else:
                                logger.warning(
                                    f"图片 {index+1}/{len(images)} 下载失败，已跳过"
                                )
                        except Exception as e:
                            logger.error(f"图片 {index+1}/{len(images)} 处理异常: {e}")
                except KeyboardInterrupt:
                    logger.info("收到中断信号，正在停止下载...")
                    executor.shutdown(wait=False)  # 立即关闭线程池，不等待所有任务完成
                    raise  # 重新抛出异常，让调用方知道下载被中断
                finally:
                    executor.shutdown(wait=False)

                logger.info(f"图片下载完成: 成功 {len(image_files)}/{len(images)} 张")
            else:
                # 本地文件夹
                folder_path = source
                if not os.path.isdir(folder_path):
                    print(f"路径不存在或不是文件夹: {folder_path}")
                    return None

                # 获取文件夹中的所有图片
                valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
                image_files = [
                    os.path.join(folder_path, f)
                    for f in os.listdir(folder_path)
                    if f.lower().endswith(valid_extensions)
                ]
                image_files.sort()

                if not image_files:
                    print(f"文件夹中没有找到图片: {folder_path}")
                    return None

                print(f"找到 {len(image_files)} 张图片")

                # 自动生成标题（默认为空）
                if title is None:
                    title = ""

                # 如果标题为空，使用文件夹名称作为标题
                if not title:
                    title = os.path.basename(folder_path)
                    print(f"使用文件夹名称作为标题: {title}")

                # 裁剪标题长度不超过32个字符
                if title and len(title) > 32:
                    title = title[:32]
                    print(f"标题超过32个字符，已裁剪为: {title}")

            # 上传图片到永久素材库
            print(f"\n开始上传 {len(image_files)} 张图片到永久素材库...")
            media_ids = []

            for i, image_path in enumerate(image_files):
                print(
                    f"处理图片 {i+1}/{len(image_files)}: {os.path.basename(image_path)}"
                )

                # 压缩图片（如果需要）
                if compress:
                    compressed_path = compressor.compress(image_path)
                    if compressed_path != image_path:
                        print(f"  图片已压缩")
                        if compressed_path not in temp_files:
                            temp_files.append(compressed_path)
                else:
                    compressed_path = image_path
                    print(f"  压缩已跳过")

                # 上传图片到永久素材库
                try:
                    result = self.push_service.material_service.add_material(
                        "image", compressed_path
                    )

                    if "media_id" in result:
                        media_ids.append(result["media_id"])
                        print(f"  上传成功，Media ID: {result['media_id']}")
                    else:
                        print(f"  上传失败: {result}")
                except Exception as e:
                    print(f"  上传失败: {e}")

            # 清理临时文件
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass

            if not media_ids:
                print("\n没有图片上传成功，无法创建草稿")
                return None

            print(f"\n成功上传 {len(media_ids)} 张图片")

            # 构建图文消息内容
            if content is None:
                # 自动生成内容，包含所有图片
                content_parts = []
                for media_id in media_ids:
                    content_parts.append(
                        f'<p><img src="{media_id}" data-media-id="{media_id}"></p>'
                    )
                content = "\n".join(content_parts)

            if digest is None:
                digest = f"共 {len(media_ids)} 张图片"

            # 确保标题不为空（如果为空，使用默认值）
            if not title:
                title = "插画集"
                print(f"标题为空，使用默认标题: {title}")

            # 最终检查标题长度，确保不超过32个字符
            if title and len(title) > 32:
                title = title[:32]
                print(f"标题超过32个字符，已裁剪为: {title}")

            # 上传标题
            print(f"上传标题: {title}")

            # 创建草稿
            print(f"\n创建草稿...")

            if is_image_message:
                # 构建图片消息
                articles = [
                    {
                        "article_type": "newspic",
                        "title": title,
                        "author": author,
                        "digest": digest,
                        "content": content,
                        "image_info": {
                            "image_list": [
                                {"image_media_id": media_id} for media_id in media_ids
                            ]
                        },
                    }
                ]
            else:
                # 图文消息
                articles = [
                    {
                        "title": title,
                        "author": author,
                        "digest": digest,
                        "content": content,
                        "thumb_media_id": media_ids[0] if media_ids else "",
                        "show_cover_pic": show_cover,
                        "need_open_comment": 0,
                        "only_fans_can_comment": 0,
                    }
                ]

            result = self.draft_service.draft_add(articles)
            if result and "media_id" in result:
                print(f"\n草稿创建成功！")
                print(f"Media ID: {result['media_id']}")
                print(f"标题: {title}")
                print(f"作者: {author}")
                print(f"图片数量: {len(media_ids)}")
                return result
            else:
                print(f"\n草稿创建失败: {result}")
                return None

        except Exception as e:
            print(f"创建草稿失败: {e}")
            import traceback

            traceback.print_exc()
            return None

    def create_draft_from_random_pixivision(
        self,
        start_page=1,
        end_page=3,
        title=None,
        author=None,
        compress=None,
        digest=None,
        content=None,
        show_cover=1,
        message_type="newspic",
    ):
        """
        从随机Pixivision插画创建草稿

        参数:
            start_page: 开始页码
            end_page: 结束页码
            title: 草稿标题
            author: 作者名称
            compress: 是否压缩图片
            digest: 图文消息摘要
            content: 图文消息内容
            show_cover: 是否显示封面图片
            message_type: 消息类型，news(图文消息)或newspic(图片消息)
        """
        try:
            # 获取已上传的article id列表
            uploaded_ids = self.upload_history.get_all_uploaded_articles()
            logger.info(f"已上传的article id数量: {len(uploaded_ids)}")

            # 随机获取一个article id
            article_id = self.pixivision_service.get_random_article_id(
                start_page, end_page, exclude_ids=uploaded_ids
            )

            if not article_id:
                print("没有可用的article id")
                return None

            print(f"随机选择了article id: {article_id}")

            # 检查是否已上传
            if self.upload_history.is_uploaded(article_id):
                print(f"Article id {article_id} 已上传过，跳过")
                return None

            # 使用article id创建草稿
            result = self.create_draft(
                article_id,
                title,
                author,
                compress,
                digest,
                content,
                show_cover,
                message_type,
            )

            # 如果创建成功，记录到上传历史
            if result and "media_id" in result:
                self.upload_history.add_uploaded_article(article_id, result["media_id"])
                print(f"已记录article id {article_id} 到上传历史")

            return result

        except Exception as e:
            print(f"从随机Pixivision插画创建草稿失败: {e}")
            import traceback

            traceback.print_exc()
            return None
