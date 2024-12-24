import os
import requests
from bs4 import BeautifulSoup
import re

# 定义请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 定义五个网址
urls = [
    "https://stock.hostmonit.com/CloudFlareYes",

]

# 解析延迟数据的正则表达式
latency_pattern = re.compile(r'(\d+(\.\d+)?)\s*(ms|毫秒)?')

# 提取表格数据的函数
def extract_table_data(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Successfully fetched data from {url}")
            print(response.text[:500])  # 打印返回的前500个字符，方便调试
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
    return None

# 处理每个网址的数据
def process_site_data(url):
    soup = extract_table_data(url)
    if not soup:
        return []

    data = []
    if "cf.090227.xyz" in url:
        print("Processing cf.090227.xyz")
        rows = soup.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:
                ip_address = columns[1].text.strip()
                latency_text = columns[2].text.strip()
                print(f"IP: {ip_address}, Latency: {latency_text}")  # 调试输出
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    data.append(ip_address)

    elif "stock.hostmonit.com" in url:
        print("Processing stock.hostmonit.com")
        rows = soup.find_all('tr', class_=re.compile(r'el-table__row'))
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:
                ip_address = columns[1].text.strip()
                latency_text = columns[2].text.strip()
                print(f"IP: {ip_address}, Latency: {latency_text}")  # 调试输出
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    data.append(ip_address)

    elif "ip.164746.xyz" in url:
        print("Processing ip.164746.xyz")
        rows = soup.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 5:
                ip_address = columns[0].text.strip()
                latency_text = columns[4].text.strip()
                print(f"IP: {ip_address}, Latency: {latency_text}")  # 调试输出
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    data.append(ip_address)

    elif "monitor.gacjie.cn" in url:
        print("Processing monitor.gacjie.cn")
        rows = soup.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 5:
                ip_address = tds[1].text.strip()
                latency_text = tds[4].text.strip()
                print(f"IP: {ip_address}, Latency: {latency_text}")  # 调试输出
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    data.append(ip_address)

    elif "345673.xyz" in url:
        print("Processing 345673.xyz")
        rows = soup.find_all('tr', class_=re.compile(r'line-cm|line-ct|line-cu'))
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 4:
                ip_address = tds[1].text.strip()
                latency_text = tds[3].text.strip()
                print(f"IP: {ip_address}, Latency: {latency_text}")  # 调试输出
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    data.append(ip_address)

    return data

# 主函数
def main():
    all_data = []
    for url in urls:
        site_data = process_site_data(url)
        all_data.extend(site_data)

    # 去除重复的IP地址
    unique_data = list(set(all_data))

    # 保存到 ip.txt 文件
    with open('ip.txt', 'w', encoding='utf-8') as f:
        for ip in unique_data:
            f.write(ip + '\n')
    print("Filtered IPs saved to ip.txt")

if __name__ == "__main__":
    main()
