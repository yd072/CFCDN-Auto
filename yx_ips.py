import requests
import re
import os
from ipwhois import IPWhois
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 预编译正则表达式
ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return ip_pattern.findall(response.text)
        else:
            logging.warning(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
    except requests.RequestException as e:
        logging.error(f"抓取网页 {url} 时发生请求错误: {e}")
        return []

def get_country_for_ip(ip, cache):
    """
    查询 IP 的国家简称，使用缓存避免重复查询
    """
    if ip in cache:
        return cache[ip]
    
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', 'Unknown')
        cache[ip] = country
        return country
    except Exception as e:
        logging.error(f"查询 {ip} 的国家代码失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ips_to_file(ips_with_country, filename='ip.txt'):
    """
    将提取的 IP 地址和国家简称保存到文件
    """
    if os.path.exists(filename):
        os.remove(filename)
    
    with open(filename, 'w') as file:
        for ip, country in sorted(ips_with_country.items()):
            file.write(f"{ip}#{country}\n")
    
    logging.info(f"提取到 {len(ips_with_country)} 个 IP 地址，已保存到 {filename}")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址及其国家简称并保存到文件
    """
    all_ips = set()
    cache = {}

    for url in urls:
        logging.info(f"正在提取 {url} 的 IP 地址...")
        ips = extract_ips_from_web(url)
        all_ips.update(ips)
    
    logging.info("正在查询 IP 的国家简称...")
    ips_with_country = {ip: get_country_for_ip(ip, cache) for ip in all_ips}

    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    target_urls = [
        "https://stock.hostmonit.com/CloudFlareYes",
    ]
    
    fetch_and_save_ips(target_urls)
