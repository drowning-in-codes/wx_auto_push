from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import time


class ScheduleManager:
    def __init__(self, config, task_func):
        self.config = config
        self.task_func = task_func
        self.scheduler = BlockingScheduler()
        self.schedule_config = config.get_schedule_config()

    def setup_schedule(self):
        weekly_frequency = self.schedule_config.get("weekly_frequency", 3)
        time_range = self.schedule_config.get(
            "time_range", {"start": "08:00", "end": "20:00"}
        )

        # 计算每周需要执行的天数
        days = self._get_random_days(weekly_frequency)

        # 解析时间范围
        start_hour, start_minute = map(int, time_range["start"].split(":"))
        end_hour, end_minute = map(int, time_range["end"].split(":"))

        # 为每个选定的天设置任务
        for day in days:
            # 在每天的随机时间执行
            hour = random.randint(start_hour, end_hour)
            minute = random.randint(0, 59)

            # 确保时间在指定范围内
            if hour == start_hour and minute < start_minute:
                minute = start_minute
            if hour == end_hour and minute > end_minute:
                minute = end_minute

            # 添加定时任务
            self.scheduler.add_job(
                self.task_func,
                CronTrigger(day_of_week=day, hour=hour, minute=minute),
                id=f"push_task_{day}",
                replace_existing=True,
            )

    def _get_random_days(self, count):
        days = [0, 1, 2, 3, 4, 5, 6]  # 0-6 对应周日到周六
        random.shuffle(days)
        return days[:count]

    def start(self):
        self.setup_schedule()
        print("调度器已启动，开始执行定时任务...")
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
        print("调度器已停止")

    def run_once(self):
        """立即执行一次任务"""
        try:
            self.task_func()
            return True
        except Exception as e:
            print(f"执行任务失败: {e}")
            return False
