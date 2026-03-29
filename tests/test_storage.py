import unittest
import os
import json
import tempfile
import shutil
from src.utils.storage.json_storage import JsonStorage
from src.utils.storage.database_storage import DatabaseStorage
from src.utils.storage.storage_factory import StorageFactory


class TestJsonStorage(unittest.TestCase):
    """JSON存储模块测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_file = os.path.join(self.temp_dir, "test_illustrations.json")
        self.storage = JsonStorage(self.storage_file)
        self.test_illustration = {
            "article_id": "12345",
            "title": "测试插画",
            "url": "https://example.com/illustration/12345",
            "description": "这是一个测试插画",
            "images": ["https://example.com/image1.jpg"],
            "tags": ["测试", "插画"],
            "category": "illustration",
            "thumbnail": "https://example.com/thumb.jpg",
        }

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_illustration(self):
        """测试保存插画"""
        result = self.storage.save_illustration(self.test_illustration)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.storage_file))

    def test_get_illustration(self):
        """测试根据ID获取插画"""
        self.storage.save_illustration(self.test_illustration)
        illustration = self.storage.get_illustration("12345")
        self.assertIsNotNone(illustration)
        self.assertEqual(illustration["title"], "测试插画")

    def test_get_illustration_not_found(self):
        """测试获取不存在的插画"""
        illustration = self.storage.get_illustration("non_existent")
        self.assertIsNone(illustration)

    def test_get_illustrations(self):
        """测试获取所有插画"""
        self.storage.save_illustration(self.test_illustration)
        illustration2 = self.test_illustration.copy()
        illustration2["article_id"] = "67890"
        illustration2["title"] = "测试插画2"
        self.storage.save_illustration(illustration2)

        illustrations = self.storage.get_illustrations()
        self.assertEqual(len(illustrations), 2)

    def test_search_illustrations(self):
        """测试搜索插画"""
        self.storage.save_illustration(self.test_illustration)
        results = self.storage.search_illustrations("测试")
        self.assertGreaterEqual(len(results), 1)

    def test_search_illustrations_by_tag(self):
        """测试根据标签搜索插画"""
        self.storage.save_illustration(self.test_illustration)
        results = self.storage.search_illustrations("插画")
        self.assertGreaterEqual(len(results), 1)

    def test_delete_illustration(self):
        """测试删除插画"""
        self.storage.save_illustration(self.test_illustration)
        result = self.storage.delete_illustration("12345")
        self.assertTrue(result)
        illustration = self.storage.get_illustration("12345")
        self.assertIsNone(illustration)

    def test_delete_illustration_not_found(self):
        """测试删除不存在的插画"""
        result = self.storage.delete_illustration("non_existent")
        self.assertFalse(result)


class TestDatabaseStorage(unittest.TestCase):
    """数据库存储模块测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")

    def tearDown(self):
        """测试后清理"""
        import time

        time.sleep(0.1)
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                pass

    def test_database_storage_init(self):
        """测试数据库存储初始化"""
        storage = DatabaseStorage(self.db_path)
        self.assertIsNotNone(storage)
        self.assertTrue(os.path.exists(self.db_path))

    def test_save_illustration(self):
        """测试保存插画"""
        storage = DatabaseStorage(self.db_path)
        test_illustration = {
            "article_id": "12345",
            "title": "测试插画",
            "url": "https://example.com/illustration/12345",
            "description": "这是一个测试插画",
            "images": ["https://example.com/image1.jpg"],
            "tags": ["测试", "插画"],
            "category": "illustration",
            "thumbnail": "https://example.com/thumb.jpg",
        }
        result = storage.save_illustration(test_illustration)
        self.assertTrue(result)

    def test_get_illustration(self):
        """测试根据ID获取插画"""
        storage = DatabaseStorage(self.db_path)
        test_illustration = {
            "article_id": "12345",
            "title": "测试插画",
            "url": "https://example.com/illustration/12345",
        }
        storage.save_illustration(test_illustration)
        illustration = storage.get_illustration("12345")
        self.assertIsNotNone(illustration)
        self.assertEqual(illustration["title"], "测试插画")


class TestStorageFactory(unittest.TestCase):
    """存储工厂测试"""

    def test_create_json_storage(self):
        """测试创建JSON存储"""
        temp_dir = tempfile.mkdtemp()
        storage_file = os.path.join(temp_dir, "test.json")
        try:
            storage = StorageFactory.create_storage("json", file_path=storage_file)
            self.assertIsInstance(storage, JsonStorage)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_create_database_storage(self):
        """测试创建数据库存储"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        try:
            storage = StorageFactory.create_storage("database", db_path=db_path)
            self.assertIsInstance(storage, DatabaseStorage)
        finally:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except PermissionError:
                    pass

    def test_create_invalid_storage(self):
        """测试创建无效存储类型"""
        storage = StorageFactory.create_storage("invalid")
        self.assertIsNone(storage)


if __name__ == "__main__":
    unittest.main()
