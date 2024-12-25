import requests
import time

def get_ip_country(ip):
    """根据 IP 获取国家简称，使用多个 API 以增加准确性"""
    print(f"查询 IP: {ip}...")
    
    # 尝试多个 API 查询，增加准确性和成功率
    apis = [
        f'http://ipinfo.io/{ip}/json',
        f'http://ip-api.com/json/{ip}',
        f'https://geolocation-db.com/json/{ip}&position=true',
    ]
    
    for api in apis:
        for attempt in range(3):  # 最大重试次数
            try:
                response = requests.get(api, timeout=10)
                response.raise_for_status()
                data = response.json()

                # 获取国家信息
                country = data.get('country', 'Unknown')
                if country != 'Unknown':
                    print(f"查询成功: {ip} -> 国家: {country}")
                    return country
                else:
                    print(f"API {api} 返回无效国家信息")
                    break  # 如果返回 'Unknown'，跳出重试循环
            except requests.RequestException as e:
                print(f"查询 {ip} 时发生错误，尝试第 {attempt+1} 次重试：{e}")
                time.sleep(2)  # 等待 2 秒后重试
                continue

    return 'Unknown'  # 如果所有 API 都失败，返回 Unknown
