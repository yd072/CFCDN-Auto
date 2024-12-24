import os
import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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
        response = requests.get(f'http://ipinfo.io/{ip_address}/json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown')
        else:
            return 'Unknown'
    except requests.RequestException:
        return 'Unknown'

# 使用 Selenium 获取动态加载的网页内容
def extract_dynamic_content(url):
    options = Options()
    options.add_argument('--headless')  # 使用无头模式
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(5)  # 等待页面加载完成
        html_content = driver.page_source
        return BeautifulSoup(html_content, 'html.parser')
    finally:
        driver.quit()

# 提取表格数据的函数
def extract_table_data(url):
    try:
        # 使用 Selenium 抓取动态网页内容
        soup = extract_dynamic_content(url)
        print(f"成功获取网页内容: {url}")
        return soup
    except Exception as e:
        print(f"请求失败: {url} - {e}")
    return None

# 处理每个网址的数据
def process_site_data(url):
    soup = extract_table_data(url)
    if not soup:
        return []

    data = []
    if "stock.hostmonit.com" in url:
        rows = soup.find_all('tr', class_=re.compile(r'el-table__row'))
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:
                ip_address = columns[1].text.strip()
                latency_text = columns[2].text.strip()
                print(f"提取到IP: {ip_address}, 延迟: {latency_text}")  # 调试信息
                latency_match = latency_pattern.match(latency_text)
                if latency_match and float(latency_match.group(1)) < 100:
                    country = get_country_code(ip_address)
                    data.append(f"{ip_address} #{country}")

    return data

# 主函数
def main():
    all_data = []
    for url in urls:
        print(f"正在处理网址: {url}")
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
