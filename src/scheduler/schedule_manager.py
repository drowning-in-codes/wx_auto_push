from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import os
import random


class ScheduleManager:
    def __init__(self, config, task_func, task_type="upload", schedule_config=None):
        self.config = config
        self.task_func = task_func
        self.task_type = task_type
        # 💡 核心修复：必须使用 APScheduler 官方标准的配置字典格式！
        scheduler_configs = {
            # 1. 配置 executors，直接在 default 字典里设置 wait_max
            "executors": {
                "default": {
                    "type": "threadpool",  # 显式指定默认执行器为线程池
                    "wait_max": 2,  # 核心：1秒呼吸一次，留出 Ctrl+C 呼吸口
                }
            },
            # 2. 配置任务默认值
            "job_defaults": {
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60,
            },
        }
        # 将规范的配置字典传给调度器
        self.scheduler = BlockingScheduler(scheduler_configs)
        self.schedule_config = schedule_config or config.get_schedule_config()
        self._stopped = False

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
                id=f"{self.task_type}_task_{day}",
                replace_existing=True,
            )

    def _get_random_days(self, count):
        days = [0, 1, 2, 3, 4, 5, 6]  # 0-6 对应周日到周六
        random.shuffle(days)
        return days[:count]

    def start(self):
        self._stopped = False
        self.setup_schedule()
        print("调度器已启动，开始执行定时任务...")
        print("按 Ctrl+C 停止服务")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n收到停止信号，正在关闭调度器...")
            self.stop(force=True)
        except Exception as e:
            print(f"调度器运行异常: {e}")
            self.stop(force=True)
            raise

    def stop(self, force=False):
        if self._stopped:
            return
        self._stopped = True

        if self.scheduler.running:
            try:
                self.scheduler.shutdown(wait=not force)
            except Exception as e:
                print(f"关闭调度器时发生异常: {e}")

        print("调度器已停止")

        if force:
            os._exit(130)

    def run_once(self):
        """立即执行一次任务"""
        try:
            self.task_func()
            return True
        except Exception as e:
            print(f"执行任务失败: {e}")
            return False

    def run_once_schedule(self):
        """
        启动调度器，执行一次任务后取消调度，不再运行后续的调度任务
        """
        print("调度器已启动，将执行一次任务后自动停止...")
        print("按 Ctrl+C 可立即停止服务")

        try:
            # 设置调度任务
            self.setup_schedule()

            # 立即执行一次任务
            print("正在执行任务...")
            try:
                self.task_func()
                print("任务执行完成")
            except Exception as e:
                print(f"任务执行失败: {e}")

            # 取消所有调度任务
            print("取消所有后续调度任务...")
            self.scheduler.remove_all_jobs()

            # 关闭调度器
            print("调度器已停止，服务已关闭")
            self.scheduler.shutdown()

        except KeyboardInterrupt:
            print("\n收到停止信号，正在关闭调度器...")
            self.scheduler.shutdown(wait=False)
            print("调度器已停止")
        except Exception as e:
            print(f"调度器运行异常: {e}")
            self.scheduler.shutdown(wait=False)
            raise
