import requests
import re
import os

def extract_ips_from_web(url):
    """
    从指定网页提取 IP 地址
    """
    try:
        # 设置请求头模拟浏览器访问
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 使用正则表达式提取 IP 地址
            return re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response.text)
        else:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def save_ips_to_file(ips, filename='ip.txt'):
    """
    将提取的 IP 地址保存到文件
    """
    # 删除已有文件，确保文件干净
    if os.path.exists(filename):
        os.remove(filename)
    
    # 写入文件
    with open(filename, 'w') as file:
        for ip in sorted(set(ips)):  # 去重并排序
            file.write(f"{ip}\n")
    
    print(f"提取到 {len(set(ips))} 个 IP 地址，已保存到 {filename}")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存到文件
    """
    all_ips = []
    for url in urls:
        print(f"正在提取 {url} 的 IP 地址...")
        ips = extract_ips_from_web(url)
        all_ips.extend(ips)
    
    save_ips_to_file(all_ips)

if __name__ == "__main__":
    # 要提取 IP 的目标 URL 列表
    target_urls = [
        "https://cf.090227.xyz",  # 示例 URL
        "https://ip.164746.xyz/ipTop10.html",  # 示例 URL
    ]
    
    # 提取 IP 并保存
    fetch_and_save_ips(target_urls)
