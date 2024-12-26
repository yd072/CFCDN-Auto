import requests
import re
import os
from bs4 import BeautifulSoup
from ipwhois import IPWhois

def get_ip_country(ip):
    """
    使用 IPWhois 查询 IP 的国家简称
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
    抓取目标网站的 IP 地址并保存到 ip.txt，格式为 IP#国家简称
    """
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',  # 添加更多目标 URL
    ]

    # 读取已存在的 IP 地址并去重
    existing_ips = set()
    if os.path.exists('ip.txt'):
        with open('ip.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('#')
                if len(parts) == 2:
                    existing_ips.add(parts[0])

    new_ips = set()

    # 从目标网站抓取 IP 地址
    for url in target_urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 使用正则表达式提取网页中的所有 IP 地址
                ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', soup.text)
                new_ips.update(ip_addresses)
        except Exception as e:
            print(f"抓取 {url} 时发生错误: {e}")

    # 去重并查询 IP 的国家
    all_ips = existing_ips.union(new_ips)
    ip_with_country = {}

    for ip in all_ips:
        country = get_ip_country(ip)
        ip_with_country[ip] = country

    # 保存 IP 和国家信息到文件
    with open('ip.txt', 'w') as file:
        for ip, country in sorted(ip_with_country.items()):  # 按 IP 排序
            file.write(f"{ip}#{country}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(ip_with_country)} 个 IP 地址")

if __name__ == '__main__':
    fetch_ips()
