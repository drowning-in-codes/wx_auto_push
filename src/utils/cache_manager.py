import json
import os
import time

try:
    import redis
except ImportError:
    redis = None


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
                        data = json.load(f)
                        # 检查是否过期
                        if "expire_at" in data:
                            if time.time() < data["expire_at"]:
                                return data["value"]
                            else:
                                # 删除过期缓存
                                os.remove(cache_file)
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
            try:
                data = {"value": value, "expire_at": time.time() + expire}
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"本地缓存写入失败: {e}")
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
        return True

    def clear(self):
        if self.cache_type == "redis" and self.redis_client:
            try:
                self.redis_client.flushdb()
                return True
            except Exception as e:
                print(f"Redis清空失败: {e}")
                return False
        else:
            # 本地缓存
            try:
                for file in os.listdir(self.cache_dir):
                    if file.endswith(".json"):
                        os.remove(os.path.join(self.cache_dir, file))
                return True
            except Exception as e:
                print(f"本地缓存清空失败: {e}")
                return False
