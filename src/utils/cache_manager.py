import json
import os
import time
import platform


try:
    import redis
except ImportError:
    redis = None


# 跨平台文件锁
if platform.system() == "Windows":
    import msvcrt

    def lock_file(f, exclusive=False):
        """Windows 文件锁定"""
        try:
            if exclusive:
                msvcrt.locking(
                    f.fileno(),
                    msvcrt.LK_NBLCK,
                    os.path.getsize(f.name) if os.path.exists(f.name) else 1,
                )
            else:
                msvcrt.locking(
                    f.fileno(),
                    msvcrt.LK_NBLCK,
                    os.path.getsize(f.name) if os.path.exists(f.name) else 1,
                )
            return True
        except (IOError, OSError):
            return False

    def unlock_file(f):
        """Windows 文件解锁"""
        try:
            msvcrt.locking(
                f.fileno(),
                msvcrt.LK_UNLCK,
                os.path.getsize(f.name) if os.path.exists(f.name) else 1,
            )
        except:
            pass

else:
    import fcntl

    def lock_file(f, exclusive=False):
        """Unix/Linux 文件锁定"""
        try:
            if exclusive:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            return False

    def unlock_file(f):
        """Unix/Linux 文件解锁"""
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except:
            pass


class CacheManager:
    def __init__(self, cache_type="local", redis_config=None, cache_dir="cache"):
        self.cache_type = cache_type
        self.redis_client = None
        self.cache_dir = cache_dir

        if cache_type == "redis" and redis:
            if redis_config is None:
                redis_config = {"host": "localhost", "port": 6379, "db": 0}
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                print("Redis连接成功")
            except Exception as e:
                print(f"Redis连接失败，切换到本地缓存: {e}")
                self.cache_type = "local"
                self.redis_client = None
        else:
            # 确保缓存目录存在
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)

    def get(self, key):
        if self.cache_type == "redis" and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"Redis读取失败: {e}")
        else:
            # 本地缓存
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        # 尝试获取文件锁（共享锁）
                        max_retries = 5
                        for attempt in range(max_retries):
                            if lock_file(f, exclusive=False):
                                break
                            if attempt < max_retries - 1:
                                time.sleep(0.05 * (attempt + 1))
                        else:
                            # 如果无法获取锁，仍然尝试读取
                            pass

                        try:
                            data = json.load(f)
                        finally:
                            unlock_file(f)

                        # 检查是否过期
                        if "expire_at" in data:
                            if time.time() < data["expire_at"]:
                                return data["value"]
                            else:
                                # 删除过期缓存
                                try:
                                    os.remove(cache_file)
                                except:
                                    pass
                except Exception as e:
                    print(f"本地缓存读取失败: {e}")
        return None

    def set(self, key, value, expire=7200):
        """
        设置缓存，默认过期时间7200秒
        """
        if self.cache_type == "redis" and self.redis_client:
            try:
                data = {"value": value, "expire_at": time.time() + expire}
                self.redis_client.set(key, json.dumps(data), ex=expire)
                return True
            except Exception as e:
                print(f"Redis写入失败: {e}")
                return False
        else:
            # 本地缓存
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            temp_file = cache_file + ".tmp"
            try:
                data = {"value": value, "expire_at": time.time() + expire}

                # 使用临时文件写入，然后重命名，避免文件损坏
                with open(temp_file, "w", encoding="utf-8") as f:
                    # 尝试获取文件锁（排他锁）
                    max_retries = 5
                    for attempt in range(max_retries):
                        if lock_file(f, exclusive=True):
                            break
                        if attempt < max_retries - 1:
                            time.sleep(0.05 * (attempt + 1))
                    else:
                        # 如果无法获取锁，仍然尝试写入
                        pass

                    try:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        f.flush()
                        os.fsync(f.fileno())
                    finally:
                        unlock_file(f)

                # 原子性重命名
                os.replace(temp_file, cache_file)
                return True
            except Exception as e:
                print(f"本地缓存写入失败: {e}")
                # 清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                return False

    def delete(self, key):
        if self.cache_type == "redis" and self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                print(f"Redis删除失败: {e}")
                return False
        else:
            # 本地缓存
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    return True
                except Exception as e:
                    print(f"本地缓存删除失败: {e}")
                    return False
