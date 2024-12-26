import requests
import re
from bs4 import BeautifulSoup

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址
    """
    try:
        response = requests.get(url)
        print(f"访问 {url}，状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 打印网页的前1000个字符，检查网页内容
            print(f"网页内容（前1000字符）: \n{response.text[:1000]}")
            
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

def save_ips_to_file(ips):
    """
    将 IP 地址保存到 ip.txt 文件中
    """
    with open('ip.txt', 'w') as file:
        for ip in sorted(ips):  # 按 IP 排序
            file.write(f"{ip}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(ips)} 个 IP 地址")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存
    """
    all_ips = set()

    # 提取所有 IP 地址
    for url in urls:
        ips = extract_ips_from_web(url)
        all_ips.update(ips)

    # 保存结果到文件
    save_ips_to_file(all_ips)

if __name__ == '__main__':
    target_urls = [
        'https://cf.090227.xyz',  # 目标 URL
    ]
    
    fetch_and_save_ips(target_urls)
