import requests
from bs4 import BeautifulSoup
import os

def fetch_ips():
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://example.com',  # 添加更多目标 URL
    ]

    existing_ips = set()
    if os.path.exists('ip.txt'):
        with open('ip.txt', 'r') as file:
            existing_ips = set(line.strip() for line in file)

    new_ips = set()

    for url in target_urls:
        print(f"正在抓取 {url} 的 IP 地址...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取 IP 地址（根据具体网站修改选择器）
            ips = set(soup.find_all(text=lambda text: text and is_valid_ip(text)))

            for ip in ips:
                new_ips.add(ip.strip())
            print(f"成功从 {url} 抓取到 {len(ips)} 个 IP 地址")
        except Exception as e:
            print(f"抓取 {url} 时发生错误: {e}")

    # 新增 IP 保存到文件
    with open('ip.txt', 'a') as file:
        for ip in new_ips - existing_ips:
            file.write(ip + '\n')

    print(f"新 IP 已保存到 ip.txt，总计新增 {len(new_ips - existing_ips)} 个 IP 地址")

def is_valid_ip(ip):
    """简单验证 IPv4 地址的正则"""
    import re
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

if __name__ == '__main__':
    fetch_ips()
