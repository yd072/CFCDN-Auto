import requests
from bs4 import BeautifulSoup
import os
import re

def fetch_ips():
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',  # 添加更多目标 URL
    ]

    # 读取已存在的 IP 地址并去重
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

            # 提取所有 IP 地址（根据具体网站修改选择器）
            ips = set(soup.find_all(text=lambda text: text and is_valid_ip(text)))

            # 将抓取到的 IP 加入新 IP 集合
            new_ips.update(ips)
            print(f"成功从 {url} 抓取到 {len(ips)} 个 IP 地址")
        except Exception as e:
            print(f"抓取 {url} 时发生错误: {e}")

    # 将新的 IP 地址去重并写入文件
    all_ips = existing_ips.union(new_ips)  # 合并已存在的和新的 IP 地址
    with open('ip.txt', 'w') as file:
        for ip in sorted(all_ips):  # 按字母顺序排序
            file.write(ip + '\n')

    print(f"新 IP 已保存到 ip.txt，总计新增 {len(new_ips)} 个 IP 地址")

def is_valid_ip(ip):
    """简单验证 IPv4 地址的正则"""
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

if __name__ == '__main__':
    fetch_ips()
