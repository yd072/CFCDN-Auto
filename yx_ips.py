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

    # 获取 IP 对应的国家简称
    ip_with_country = {}
    for ip in new_ips:
        country = get_ip_country(ip)
        ip_with_country[ip] = country
        print(f"IP: {ip} -> 国家: {country}")

    # 将新的 IP 地址去重并写入文件
    all_ips = existing_ips.union(ip_with_country.keys())  # 合并已存在的和新的 IP 地址
    print(f"合并后的所有 IP 地址（去重后）：{all_ips}")

    with open('ip.txt', 'w') as file:
        for ip in sorted(all_ips):  # 按字母顺序排序
            # 输出格式：IP#国家简称（没有空格）
            file.write(f"{ip}#{ip_with_country.get(ip, 'Unknown')}\n")

    print(f"新 IP 已保存到 ip.txt，总计新增 {len(new_ips)} 个 IP 地址")

def is_valid_ip(ip):
    """简单验证 IPv4 地址的正则"""
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

def is_cloudflare_ip(ip):
    """检查 IP 是否属于 Cloudflare"""
    cloudflare_ips = [
        '104.16.0.0', '104.17.0.0', '104.18.0.0', '104.19.0.0',
        '104.20.0.0', '104.21.0.0', '104.22.0.0', '104.23.0.0', 
        '104.24.0.0', '104.25.0.0'
    ]
    return ip.startswith(tuple(cloudflare_ips))

def get_ip_country(ip):
    """根据 IP 获取国家简称，使用多个 API 以增加准确性"""
    print(f"查询 IP: {ip}...")

    # 如果是 Cloudflare IP，则标记为 CDN
    if is_cloudflare_ip(ip):
        return 'CDN'

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

if __name__ == '__main__':
    fetch_ips()
