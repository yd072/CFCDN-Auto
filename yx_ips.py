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

# 获取IP地址的国家代码
def get_country_code(ip_address):
    try:
        # 通过 ipinfo.io API 获取IP的地理位置信息
        response = requests.get(f'http://ipinfo.io/{ip_address}/json')
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown')
        else:
            return 'Unknown'
    except requests.RequestException:
        return 'Unknown'

# 提取表格数据的函数
def extract_table_data(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            print(f"无法从 {url} 获取数据。状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"请求失败: {url} - {e}")
    return None

# 处理每个网址的数据
def process_site_data(url):
    soup = extract_table_data(url)
    if not soup:
        return []

    data = []
    if "cf.090227.xyz" in url:
        rows = soup.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:
                ip_address = columns[1].text.strip()
                latency_text = columns[2].text.strip()
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    country = get_country_code(ip_address)
                    data.append(f"{ip_address} #{country}")

    elif "stock.hostmonit.com" in url:
        rows = soup.find_all('tr', class_=re.compile(r'el-table__row'))
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:
                ip_address = columns[1].text.strip()
                latency_text = columns[2].text.strip()
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    country = get_country_code(ip_address)
                    data.append(f"{ip_address} #{country}")

    elif "ip.164746.xyz" in url:
        rows = soup.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 5:
                ip_address = columns[0].text.strip()
                latency_text = columns[4].text.strip()
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    country = get_country_code(ip_address)
                    data.append(f"{ip_address} #{country}")

    elif "monitor.gacjie.cn" in url:
        rows = soup.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 5:
                ip_address = tds[1].text.strip()
                latency_text = tds[4].text.strip()
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    country = get_country_code(ip_address)
                    data.append(f"{ip_address} #{country}")

    elif "345673.xyz" in url:
        rows = soup.find_all('tr', class_=re.compile(r'line-cm|line-ct|line-cu'))
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 4:
                ip_address = tds[1].text.strip()
                latency_text = tds[3].text.strip()
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    country = get_country_code(ip_address)
                    data.append(f"{ip_address} #{country}")

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
        for entry in unique_data:
            f.write(entry + '\n')
    print("筛选后的IP及国家代码已保存到 ip.txt 文件")

if __name__ == "__main__":
    main()
