#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试调度器是否能正确响应Ctrl+C
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import Config
from src.scheduler.schedule_manager import ScheduleManager

def test_task():
    """测试任务函数"""
    print("执行测试任务...")
    time.sleep(2)
    print("测试任务完成")

if __name__ == "__main__":
    config = Config()
    
    print("测试调度器Ctrl+C响应")
    print("按 Ctrl+C 停止测试")
    
    try:
        schedule_manager = ScheduleManager(config, test_task)
        schedule_manager.start()
    except KeyboardInterrupt:
        print("\n测试已停止")
        if schedule_manager:
            schedule_manager.stop()
    except Exception as e:
        print(f"测试异常: {e}")
        if schedule_manager:
            schedule_manager.stop()