import requests
import os


def download_pixiv_image(url, output_path):
    """
    下载Pixiv图片
    :param url: 图片URL
    :param output_path: 输出文件路径
    :return: 下载是否成功
    """
    try:
        # 设置请求头，添加Referer和其他浏览器标识
        headers = {
            "Referer": "https://www.pixiv.net/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        print(f"正在下载: {url}")
        print(f"保存到: {output_path}")

        # 发送请求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # 检查请求是否成功

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存图片
        with open(output_path, "wb") as f:
            f.write(response.content)

        print("✓ 下载成功")
        return True
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False


if __name__ == "__main__":
    # 测试图片URL
    image_url = "https://i.pximg.net/c/260x260_80/img-master/img/2025/12/05/16/05/02/138250092_p0_square1200.jpg"

    # 输出路径
    output_dir = "./test_downloads"
    output_filename = "test_pixiv_image.jpg"
    output_path = os.path.join(output_dir, output_filename)

    # 下载图片
    download_pixiv_image(image_url, output_path)

    # 验证文件是否存在
    if os.path.exists(output_path):
        print(f"✓ 图片已保存到: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")
    else:
        print("✗ 图片保存失败")
