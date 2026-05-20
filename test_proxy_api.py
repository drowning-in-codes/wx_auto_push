import requests

# 测试直接访问代理池 API
api_url = "https://proxy.scdn.io/api/get_proxy.php"
params = {
    "protocol": "all",
    "count": 5,
    "country_code": ""
}

try:
    # 禁用系统代理，直接连接
    session = requests.Session()
    session.trust_env = False
    response = session.get(api_url, params=params, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error: {e}")
