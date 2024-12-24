from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# 设置无头模式，使用 Selenium 启动浏览器
def extract_table_data_selenium(url):
    options = Options()
    options.add_argument("--headless")  # 不打开浏览器窗口，后台运行
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # 等待页面加载完成

        # 获取渲染后的页面源代码
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error loading page with Selenium: {e}")
        return None
    finally:
        driver.quit()

# 处理每个网址的数据
def process_site_data(url):
    print(f"Processing URL: {url}")
    soup = extract_table_data_selenium(url)
    if not soup:
        print(f"No data found for {url}")
        return []

    data = []
    try:
        rows = soup.find_all('tr', class_=re.compile(r'el-table__row'))
        print(f"Found {len(rows)} rows in stock.hostmonit.com")
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:
                ip_address = columns[1].text.strip()  # 提取 IP 地址
                print(f"Extracted IP: {ip_address}")  # 打印提取的 IP 地址
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
