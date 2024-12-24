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
import traceback

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

urls = [
    "https://stock.hostmonit.com/CloudFlareYes",
]

latency_pattern = re.compile(r'(\d+(\.\d+)?)\s*(ms|毫秒)?')

def get_country_code(ip_address):
    try:
        response = requests.get(f'http://ipinfo.io/{ip_address}/json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown')
        else:
            return 'Unknown'
    except requests.RequestException as e:
        print(f"获取国家代码失败: {ip_address} - {e}")
        return 'Unknown'

def extract_dynamic_content(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service('/path/to/chromedriver')  # 替换为实际路径
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        print(f"成功打开网址: {url}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'el-table__row'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(f"页面加载完成，提取内容如下:\n{soup.prettify()[:1000]}")  # 打印部分 HTML
        return soup
    except Exception as e:
        print(f"加载动态内容失败: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

def process_site_data(url):
    soup = extract_dynamic_content(url)
    if not soup:
        print(f"无法提取网址内容: {url}")
        return []

    data = []
    try:
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
    except Exception as e:
        print(f"处理数据时出错: {e}")
        traceback.print_exc()

    return data

def main():
    try:
        all_data = []
        for url in urls:
            print(f"正在处理网址: {url}")
            site_data = process_site_data(url)
            all_data.extend(site_data)

        unique_data = list(set(all_data))

        with open('ip.txt', 'w', encoding='utf-8') as f:
            for entry in unique_data:
                f.write(entry + '\n')
        print("筛选后的IP及国家代码已保存到 ip.txt 文件")
    except Exception as e:
        print("程序出错！")
        traceback.print_exc()

if __name__ == "__main__":
    main()
