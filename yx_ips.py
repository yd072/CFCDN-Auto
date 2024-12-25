import requests
from bs4 import BeautifulSoup
import os
import re
import time

def fetch_ips():
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',  # 添加更多目标 URL
    ]

    # 读取已存在的 IP 地址并去重
    existing_ips = set()
    if os.path.exists('ip.txt'):
        with open('ip.txt', 'r') as file:
            existing_ips = set(line.strip().split('#')[0] for line in file)

    new_ips = set()

    for url in target_urls:
        print(f"正在抓取 {url} 的 IP 地址...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取所有 IP 地址（根据具体网站修改选择器）
            ips = set(soup.find_all(text=lambda text: text and is_valid_ip(text)))

            # 将抓取到的 IP 加入新 IP 集合
            new_ips.update(ips)
            print(f"成功从 {url} 抓取到 {len(ips)} 个 IP 地址")
        except Exception as e:
            print(f"抓取 {url} 时发生错误: {e}")

    # 获取 IP 对应的地区简称
    ip_with_region = {}
    for ip in new_ips:
        region = get_ip_region(ip)
        ip_with_region[ip] = region
        print(f"IP: {ip} -> 地区: {region}")

    # 将新的 IP 地址去重并写入文件
    all_ips = existing_ips.union(ip_with_region.keys())  # 合并已存在的和新的 IP 地址
    print(f"合并后的所有 IP 地址（去重后）：{all_ips}")

    with open('ip.txt', 'w') as file:
        for ip in sorted(all_ips):  # 按字母顺序排序
            # 输出格式：IP#地区简称（没有空格）
            file.write(f"{ip}#{ip_with_region.get(ip, 'Unknown')}\n")

    print(f"新 IP 已保存到 ip.txt，总计新增 {len(new_ips)} 个 IP 地址")

def is_valid_ip(ip):
    """简单验证 IPv4 地址的正则"""
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

def get_ip_region(ip):
    """根据 IP 获取地区简称，使用多个 API 以增加准确性"""
    print(f"查询 IP: {ip}...")

    apis = [
        f'http://ipinfo.io/{ip}/json',
        f'http://ip-api.com/json/{ip}',
        f'https://geolocation-db.com/json/{ip}&position=true',
        f'https://ip-api.io/{ip}/json',  # 额外添加一个 API
    ]
    
    for api in apis:
        for attempt in range(3):  # 最大重试次数
            try:
                response = requests.get(api, timeout=10)
                response.raise_for_status()
                data = response.json()

                # 获取地区信息
                region = data.get('country', 'Unknown')
                if region != 'Unknown':
                    print(f"查询成功: {ip} -> 地区: {region}")
                    return region
                else:
                    print(f"API {api} 返回无效地区信息")
                    break  # 如果返回 'Unknown'，跳出重试循环
            except requests.RequestException as e:
                print(f"查询 {ip} 时发生错误，尝试第 {attempt+1} 次重试：{e}")
                time.sleep(2)  # 等待 2 秒后重试
                continue

    return 'Unknown'  # 如果所有 API 都失败，返回 Unknown

if __name__ == '__main__':
    fetch_ips()
