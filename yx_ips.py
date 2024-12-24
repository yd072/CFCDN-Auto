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
    "https://stock.hostmonit.com/CloudFlareYes",  # 示例 URL
]

# 定义延迟数据的正则表达式
latency_pattern = re.compile(r'(\d+(\.\d+)?)\s*(ms|毫秒|milliseconds|秒)?')

# 提取表格数据的函数
def extract_table_data(url):
    try:
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        
        # 打印请求的状态码和网页的前500个字符，确认请求是否成功
        print(f"Request to {url} returned status code {response.status_code}")
        print(f"First 500 characters of page content:\n{response.text[:500]}")  # 打印前500字符

        if response.status_code == 200:
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
        # 针对 stock.hostmonit.com 网站
        if "stock.hostmonit.com" in url:
            rows = soup.find_all('tr', class_=re.compile(r'el-table__row'))
            print(f"Found {len(rows)} rows in stock.hostmonit.com")  # 打印找到的行数
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 3:
                    ip_address = columns[1].text.strip()  # 提取 IP 地址
                    latency_text = columns[2].text.strip()  # 提取延迟
                    latency_match = latency_pattern.match(latency_text)
                    if latency_match:
                        print(f"Extracted IP: {ip_address} with latency: {latency_text}")  # 打印提取的 IP 地址和延迟
                        data.append(ip_address)
        else:
            print(f"URL not matched for IP extraction: {url}")

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
