#!/usr/bin/env python3
"""
测试下载图片时Ctrl+C是否可以打断
"""
import os
import sys
import logging
from src.push.pixivision_service import PixivisionService
from src.utils.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_download_ctrl_c():
    """测试下载图片时Ctrl+C是否可以打断"""
    print("测试下载图片时Ctrl+C是否可以打断")
    print("按 Ctrl+C 测试是否能中断下载")
    
    # 加载配置
    config = Config()
    proxy_config = config.get_proxy_config()
    request_config = config.get_request_config()
    download_config = config.get_download_config()
    
    # 创建PixivisionService实例
    pixivision_service = PixivisionService(
        proxy_config=proxy_config,
        request_config=request_config
    )
    
    # 测试下载一个插画的图片
    illustration_id = "11472"  # 一个示例插画ID
    download_dir = os.path.join(os.getcwd(), "test_download")
    
    try:
        print(f"开始下载插画 {illustration_id} 的图片...")
        print(f"下载目录: {download_dir}")
        print("按 Ctrl+C 测试是否能中断下载")
        
        # 开始下载
        success, download_path, downloaded_files = pixivision_service.download_illustration_images(
            illustration_id=illustration_id,
            download_dir=download_dir,
            max_retries=3,
            max_workers=5
        )
        
        if success:
            print(f"下载成功，共下载 {len(downloaded_files)} 张图片")
            print(f"下载路径: {download_path}")
        else:
            print("下载失败")
    except KeyboardInterrupt:
        print("\n下载已被用户中断")
        return True
    except Exception as e:
        print(f"下载过程中出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_download_ctrl_c()
