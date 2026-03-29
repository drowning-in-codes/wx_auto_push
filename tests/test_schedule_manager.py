import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, time
from src.scheduler.schedule_manager import ScheduleManager


class TestScheduleManager(unittest.TestCase):
    """调度管理模块测试"""

    def setUp(self):
        """测试前准备"""
        self.mock_task_func = Mock()
        self.mock_config = Mock()
        self.mock_config.get_schedule_config.return_value = {
            "weekly_frequency": 3,
            "time_range": {"start": "08:00", "end": "20:00"},
        }
        self.schedule_manager = ScheduleManager(self.mock_config, self.mock_task_func)

    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.schedule_manager.config)
        self.assertIsNotNone(self.schedule_manager.task_func)
        self.assertIsNotNone(self.schedule_manager.scheduler)

    def test_get_random_days(self):
        """测试获取随机执行日期"""
        days = self.schedule_manager._get_random_days(3)
        self.assertEqual(len(days), 3)
        for day in days:
            self.assertIn(day, range(7))

    @patch("src.scheduler.schedule_manager.BlockingScheduler")
    def test_setup_schedule(self, mock_scheduler_class):
        """测试设置调度"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        schedule_manager = ScheduleManager(self.mock_config, self.mock_task_func)
        schedule_manager.scheduler = mock_scheduler
        schedule_manager.setup_schedule()

        mock_scheduler.add_job.assert_called()

    @patch("src.scheduler.schedule_manager.BlockingScheduler")
    def test_start(self, mock_scheduler_class):
        """测试启动调度器"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        schedule_manager = ScheduleManager(self.mock_config, self.mock_task_func)
        schedule_manager.scheduler = mock_scheduler
        schedule_manager.start()

        mock_scheduler.start.assert_called_once()

    @patch("src.scheduler.schedule_manager.BlockingScheduler")
    def test_stop(self, mock_scheduler_class):
        """测试停止调度器"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        schedule_manager = ScheduleManager(self.mock_config, self.mock_task_func)
        schedule_manager.scheduler = mock_scheduler
        schedule_manager.stop()

        mock_scheduler.shutdown.assert_called_once()


if __name__ == "__main__":
    unittest.main()
