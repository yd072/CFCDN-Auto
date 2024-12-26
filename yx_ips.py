import requests
from bs4 import BeautifulSoup
import re

def extract_ips_from_web(url):
    """
    使用 requests 获取网页内容并提取所有 IP 地址
    """
    try:
        # 发送 HTTP 请求获取网页内容
        print(f"正在访问 {url} ...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        
        # 检查响应状态
        if response.status_code != 200:
            print(f"无法访问 {url}，状态码: {response.status_code}")
            return []

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取页面中的所有文本
        text = soup.get_text()

        # 使用正则表达式提取 IP 地址
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_addresses = re.findall(ip_pattern, text)

        if not ip_addresses:
            print(f"未从 {url} 提取到任何 IP 地址")
        else:
            print(f"从 {url} 提取到 {len(ip_addresses)} 个 IP 地址")
        
        return ip_addresses

    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def save_ips_to_file(ips):
    """
    将 IP 地址保存到 ip.txt 文件中
    """
    with open('ip.txt', 'w') as file:
        for ip in sorted(set(ips)):  # 去重并按 IP 排序
            file.write(f"{ip}\n")
    
    print(f"IP 地址已保存到 ip.txt，总计 {len(set(ips))} 个 IP 地址")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存
    """
    all_ips = []

    # 提取所有 IP 地址
    for url in urls:
        ips = extract_ips_from_web(url)
        all_ips.extend(ips)

    # 保存结果到文件
    save_ips_to_file(all_ips)

if __name__ == '__main__':
    target_urls = [
        'https://ip.164746.xyz/ipTop10.html',  # 示例 URL 1
        'https://cf.090227.xyz',              # 示例 URL 2
    ]
    
    fetch_and_save_ips(target_urls)
