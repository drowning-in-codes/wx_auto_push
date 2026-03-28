import os
import tempfile
from PIL import Image
import io


class ImageCompressor:
    """
    图片压缩服务
    用于在上传前自动压缩超过限制的图片
    """

    # 默认限制（字节）
    DEFAULT_MAX_SIZE = 1 * 1024 * 1024  # 1MB，微信图文消息内图片限制
    DEFAULT_MAX_DIMENSION = 2000  # 最大边长

    def __init__(self, max_size=None, max_dimension=None, quality=85):
        """
        初始化图片压缩器

        参数:
            max_size: 最大文件大小（字节），默认1MB
            max_dimension: 最大边长（像素），默认2000
            quality: JPEG压缩质量（1-100），默认85
        """
        self.max_size = max_size or self.DEFAULT_MAX_SIZE
        self.max_dimension = max_dimension or self.DEFAULT_MAX_DIMENSION
        self.quality = quality

    def compress(self, image_path, output_path=None):
        """
        压缩图片

        参数:
            image_path: 输入图片路径
            output_path: 输出图片路径，如果不指定则创建临时文件

        返回:
            压缩后的图片路径
        """
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size <= self.max_size:
            # 文件大小符合要求，检查尺寸
            with Image.open(image_path) as img:
                width, height = img.size
                if max(width, height) <= self.max_dimension:
                    # 尺寸也符合要求，直接返回原图
                    return image_path

        # 需要压缩
        if output_path is None:
            # 创建临时文件
            suffix = os.path.splitext(image_path)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                output_path = f.name

        # 打开图片
        with Image.open(image_path) as img:
            # 转换为RGB模式（处理RGBA等模式）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 调整尺寸
            width, height = img.size
            if max(width, height) > self.max_dimension:
                ratio = self.max_dimension / max(width, height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"图片尺寸已调整: {width}x{height} -> {new_width}x{new_height}")

            # 压缩质量直到文件大小符合要求
            quality = self.quality
            min_quality = 30  # 最低质量

            while quality >= min_quality:
                # 保存到内存
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                compressed_size = buffer.tell()

                if compressed_size <= self.max_size:
                    # 文件大小符合要求，保存到文件
                    with open(output_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    print(f"图片已压缩: {file_size / 1024:.1f}KB -> {compressed_size / 1024:.1f}KB (质量: {quality})")
                    return output_path

                # 降低质量继续尝试
                quality -= 5

            # 如果质量降到最低仍然超过限制，强制保存
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=min_quality, optimize=True)
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
            print(f"警告: 图片压缩后仍超过限制，已使用最低质量保存")
            return output_path

    def compress_to_size(self, image_path, target_size=None):
        """
        压缩图片到指定大小

        参数:
            image_path: 输入图片路径
            target_size: 目标文件大小（字节），默认使用初始化时设置的大小

        返回:
            压缩后的图片路径（临时文件）
        """
        target_size = target_size or self.max_size

        # 创建临时文件
        suffix = os.path.splitext(image_path)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            output_path = f.name

        return self.compress(image_path, output_path)

    @staticmethod
    def get_image_info(image_path):
        """
        获取图片信息

        参数:
            image_path: 图片路径

        返回:
            包含文件大小、尺寸、格式的字典
        """
        file_size = os.path.getsize(image_path)
        with Image.open(image_path) as img:
            width, height = img.size
            format_type = img.format
            mode = img.mode

        return {
            'file_size': file_size,
            'file_size_kb': file_size / 1024,
            'file_size_mb': file_size / (1024 * 1024),
            'width': width,
            'height': height,
            'format': format_type,
            'mode': mode
        }

    def cleanup(self, temp_path):
        """
        清理临时文件

        参数:
            temp_path: 临时文件路径
        """
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
