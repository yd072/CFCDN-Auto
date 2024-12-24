import os
import requests
from bs4 import BeautifulSoup
import re

# 定义请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://example.com',
}

# 定义目标网址
urls = [
    "https://stock.hostmonit.com/CloudFlareYes",
]

# 定义延迟数据的正则表达式
latency_pattern = re.compile(r'(\d+(\.\d+)?)\s*(ms|毫秒|milliseconds|秒)?')

# 提取表格数据的函数
def extract_table_data(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Successfully fetched data from {url}")  # 调试输出
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
    return None

# 处理每个网址的数据
def process_site_data(url):
    print(f"Processing URL: {url}")
    soup = extract_table_data(url)
    if not soup:
        print(f"No data found for {url}")
        return []

    data = []
    try:
        # 打印 HTML 内容的前 500 个字符，检查页面结构
        print(f"Page content preview:\n{soup.prettify()[:500]}")

        # 针对 stock.hostmonit.com 网站
        if "stock.hostmonit.com" in url:
            rows = soup.find_all('tr', class_=re.compile(r'el-table__row'))
            print(f"Found {len(rows)} rows in stock.hostmonit.com")  # 打印找到的行数
            if not rows:
                print("No rows found. Check page structure.")
            for row in rows:
                columns = row.find_all('td')
                print(f"Row data: {[column.text.strip() for column in columns]}")  # 打印每行的列数据
                if len(columns) >= 3:
                    ip_address = columns[1].text.strip()
                    latency_text = columns[2].text.strip()
                    print(f"IP Address: {ip_address}, Latency: {latency_text}")  # 打印 IP 地址和延迟
                    latency_match = latency_pattern.match(latency_text)
                    if latency_match and float(latency_match.group(1)) < 100:
                        data.append(ip_address)

    except Exception as e:
        print(f"Error processing {url}: {e}")

    return data

# 主函数
def main():
    all_data = []
    for url in urls:
        site_data = process_site_data(url)
        all_data.extend(site_data)

    # 去重并保存到文件
    unique_data = list(set(all_data))
    if unique_data:
        with open('ip.txt', 'w', encoding='utf-8') as f:
            for ip in unique_data:
                f.write(ip + '\n')
        print("Filtered IPs saved to ip.txt")
    else:
        print("No IPs found.")

if __name__ == "__main__":
    main()
