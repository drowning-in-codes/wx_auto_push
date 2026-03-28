import unittest
import os
import tempfile
from PIL import Image
from src.utils.image_compressor import ImageCompressor


class TestImageCompressor(unittest.TestCase):
    """图片压缩模块测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.compressor = ImageCompressor(
            max_size=1024 * 1024,
            max_dimension=2000,
            quality=85
        )
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        self._create_test_image(self.test_image_path, (3000, 2000))

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def _create_test_image(self, path, size, color=(255, 0, 0)):
        """创建测试图片"""
        img = Image.new('RGB', size, color)
        img.save(path, 'JPEG')

    def test_compress_small_image(self):
        """测试压缩小图片（不需要压缩）"""
        small_image_path = os.path.join(self.temp_dir, "small_image.jpg")
        self._create_test_image(small_image_path, (100, 100))

        result = self.compressor.compress(small_image_path)
        self.assertEqual(result, small_image_path)

    def test_compress_large_image(self):
        """测试压缩大图片"""
        result = self.compressor.compress(self.test_image_path)
        self.assertIsNotNone(result)

        if result != self.test_image_path:
            self.assertTrue(os.path.exists(result))
            with Image.open(result) as img:
                self.assertLessEqual(max(img.size), 2000)

    def test_compress_exceeds_max_size(self):
        """测试压缩超大图片"""
        large_image_path = os.path.join(self.temp_dir, "large_image.jpg")
        self._create_test_image(large_image_path, (5000, 5000))

        result = self.compressor.compress(large_image_path)
        self.assertIsNotNone(result)

        if result != large_image_path:
            file_size = os.path.getsize(result)
            self.assertLessEqual(file_size, 1024 * 1024)

    def test_compress_nonexistent_image(self):
        """测试压缩不存在的图片"""
        result = self.compressor.compress("nonexistent_image.jpg")
        self.assertEqual(result, "nonexistent_image.jpg")

    def test_compress_with_different_quality(self):
        """测试不同压缩质量"""
        compressor = ImageCompressor(
            max_size=1024 * 1024,
            max_dimension=2000,
            quality=50
        )

        result = compressor.compress(self.test_image_path)
        self.assertIsNotNone(result)

    def test_compress_png_image(self):
        """测试压缩PNG图片"""
        png_image_path = os.path.join(self.temp_dir, "test_image.png")
        img = Image.new('RGB', (3000, 2000), (0, 255, 0))
        img.save(png_image_path, 'PNG')

        result = self.compressor.compress(png_image_path)
        self.assertIsNotNone(result)

    def test_get_image_size(self):
        """测试获取图片大小"""
        size = self.compressor.get_image_size(self.test_image_path)
        self.assertGreater(size, 0)

    def test_get_image_dimensions(self):
        """测试获取图片尺寸"""
        dimensions = self.compressor.get_image_dimensions(self.test_image_path)
        self.assertEqual(dimensions, (3000, 2000))

    def test_should_compress(self):
        """测试判断是否需要压缩"""
        small_image_path = os.path.join(self.temp_dir, "small_image.jpg")
        self._create_test_image(small_image_path, (100, 100))

        should_compress = self.compressor.should_compress(small_image_path)
        self.assertFalse(should_compress)

        should_compress = self.compressor.should_compress(self.test_image_path)
        self.assertTrue(should_compress)


if __name__ == '__main__':
    unittest.main()
