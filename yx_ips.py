import re
import os
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

def save_ips_to_file(ips):
    """
    将 IP 地址和其对应的国家信息保存到 ip.txt 文件中
    格式为 IP#国家简称
    """
    ip_with_country = {}

    # 查询每个 IP 地址的国家简称
    for ip in ips:
        country = get_ip_country(ip)
        ip_with_country[ip] = country

    # 保存结果到文件
    with open('ip.txt', 'w') as file:
        for ip, country in sorted(ip_with_country.items()):  # 按 IP 排序
            file.write(f"{ip}#{country}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(ip_with_country)} 个 IP 地址")

def is_valid_ip(ip):
    """验证是否是有效的 IPv4 地址"""
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

def fetch_and_save_ips(ips):
    """
    过滤有效 IP 地址并保存
    """
    valid_ips = [ip for ip in ips if is_valid_ip(ip)]
    save_ips_to_file(valid_ips)

if __name__ == '__main__':
    # 假设有一些 IP 地址列表，实际使用时可以替换为你获取的 IP 列表
    ip_addresses = [
        '192.168.1.1',
        '8.8.8.8',
        '123.45.67.89',
        '10.0.0.1'
    ]

    # 执行保存操作
    fetch_and_save_ips(ip_addresses)
