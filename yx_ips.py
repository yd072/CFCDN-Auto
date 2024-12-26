import requests
import re
from ipwhois import IPWhois
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_ip_country(ip, ip_cache):
    """
    查询 IP 的国家简称，缓存查询结果避免重复查询
    """
    # 如果 IP 已经查询过，直接返回缓存结果
    if ip in ip_cache:
        return ip_cache[ip]
    
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', 'Unknown')
        country = country if country else 'Unknown'
        
        # 缓存查询结果
        ip_cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 的国家代码失败: {e}")
        ip_cache[ip] = 'Unknown'
        return 'Unknown'

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 使用正则表达式提取所有 IP 地址
            ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', soup.text)
            
            if not ip_addresses:
                print(f"未从 {url} 提取到任何 IP 地址")
            return ip_addresses
        else:
            print(f"无法访问网页 {url}, 状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def save_ips_to_file(ips_with_country):
    """
    将 IP 地址和其对应的国家信息保存到 ip.txt 文件中
    """
    with open('ip.txt', 'w') as file:
        for ip, country in sorted(ips_with_country.items()):  # 按 IP 排序
            file.write(f"{ip}#{country}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(ips_with_country)} 个 IP 地址")

def is_valid_ip(ip):
    """验证是否是有效的 IPv4 地址"""
    return re.match(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', ip)

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存
    """
    all_ips = set()
    ip_cache = {}

    # 提取所有 IP 地址
    for url in urls:
        ips = extract_ips_from_web(url)
        all_ips.update(ips)

    # 过滤有效 IP 地址并使用并发查询国家信息
    valid_ips = [ip for ip in all_ips if is_valid_ip(ip)]
    
    # 使用线程池并发查询国家信息
    ips_with_country = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_ip_country, ip, ip_cache): ip for ip in valid_ips}
        for future in as_completed(futures):
            ip = futures[future]
            country = future.result()
            ips_with_country[ip] = country

    # 保存结果到文件
    save_ips_to_file(ips_with_country)

if __name__ == '__main__':
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',
    ]
    
    fetch_and_save_ips(target_urls)
