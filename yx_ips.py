from ipwhois import IPWhois
import requests
import re
import os
from bs4 import BeautifulSoup

def is_valid_ip(ip):
    """验证是否是有效的 IPv4 地址"""
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

def get_ip_country(ip):
    """
    使用 ipwhois 查询 IP 的国家代码
    """
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', 'Unknown')
        return country if country else 'Unknown'
    except Exception as e:
        print(f"查询 {ip} 的国家代码失败: {e}")
        return 'Unknown'

def fetch_ips():
    """
    抓取目标网站的 IP 地址并查询国家代码
    """
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',  # 添加更多目标 URL
    ]

    # 读取已存在的 IP 地址并去重
    existing_ips = {}
    if os.path.exists('ip.txt'):
        with open('ip.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('#')
                if len(parts) == 2:
                    existing_ips[parts[0]] = parts[1]

    new_ips = set()

    # 抓取 IP 地址
    for url in target_urls:
        print(f"正在抓取 {url} 的 IP 地址...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取 IP 地址
            ips = set(soup.find_all(text=lambda text: text and is_valid_ip(text)))
            new_ips.update(ips)
            print(f"从 {url} 抓取到 {len(ips)} 个 IP 地址")
        except Exception as e:
            print(f"抓取 {url} 时发生错误: {e}")

    # 查询 IP 对应的国家代码
    ip_with_country = {}
    for ip in new_ips:
        if ip not in existing_ips:
            country = get_ip_country(ip)
            ip_with_country[ip] = country
            print(f"IP: {ip} -> 国家代码: {country}")
        else:
            ip_with_country[ip] = existing_ips[ip]  # 已有的国家代码直接复用

    # 保存结果到文件
    all_ips = {**existing_ips, **ip_with_country}
    with open('ip.txt', 'w') as file:
        for ip, country in sorted(all_ips.items()):  # 按 IP 排序
            file.write(f"{ip}#{country}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(all_ips)} 个 IP 地址")

if __name__ == '__main__':
    fetch_ips()
