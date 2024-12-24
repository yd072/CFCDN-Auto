import os
import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 定义请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 定义目标网址
urls = [
    "https://stock.hostmonit.com/CloudFlareYes",
]

# 正则表达式解析延迟数据
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

# 使用 Selenium 动态加载网页内容
def extract_dynamic_content(url):
    # 配置 Selenium 的 Chrome 驱动
    options = Options()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service('/path/to/chromedriver')  # 替换为 chromedriver 的路径
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        # 等待表格加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'el-table__row'))
        )
        html_content = driver.page_source
        return BeautifulSoup(html_content, 'html.parser')
    finally:
        driver.quit()

# 提取表格数据
def extract_table_data(url):
    try:
        soup = extract_dynamic_content(url)
        print(f"成功加载网页内容: {url}")
        return soup
    except Exception as e:
        print(f"无法加载网页内容: {url} - 错误: {e}")
    return None

# 处理目标网站数据
def process_site_data(url):
    soup = extract_table_data(url)
    if not soup:
        return []

    data = []
    # 处理 CloudFlareYes 的表格数据
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

    # 去重处理
    unique_data = list(set(all_data))

    # 保存到 ip.txt 文件
    with open('ip.txt', 'w', encoding='utf-8') as f:
        for entry in unique_data:
            f.write(entry + '\n')
    print("筛选后的IP及国家代码已保存到 ip.txt 文件")

if __name__ == "__main__":
    main()
