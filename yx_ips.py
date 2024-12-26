from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

def extract_ips_from_web(url):
    """
    使用 Selenium 获取网页内容并提取所有 IP 地址
    """
    try:
        # 设置 Chrome 配置，避免打开浏览器窗口
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
        driver = webdriver.Chrome(options=chrome_options)  # 指定 ChromeDriver 路径
        driver.get(url)

        # 等待页面加载完成
        driver.implicitly_wait(5)  # 等待最多 5 秒

        # 获取页面的 HTML 内容
        page_source = driver.page_source

        # 解析页面
        soup = BeautifulSoup(page_source, 'html.parser')

        # 使用正则表达式提取所有 IP 地址
        ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', soup.text)

        if not ip_addresses:
            print(f"未从 {url} 提取到任何 IP 地址")
        
        driver.quit()  # 退出浏览器
        return ip_addresses

    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def save_ips_to_file(ips):
    """
    将 IP 地址保存到 ip.txt 文件中
    """
    with open('ip.txt', 'w') as file:
        for ip in sorted(ips):  # 按 IP 排序
            file.write(f"{ip}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(ips)} 个 IP 地址")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存
    """
    all_ips = set()

    # 提取所有 IP 地址
    for url in urls:
        ips = extract_ips_from_web(url)
        all_ips.update(ips)

    # 保存结果到文件
    save_ips_to_file(all_ips)

if __name__ == '__main__':
    target_urls = [
        'https://cf.090227.xyz',  # 目标 URL
    ]
    
    fetch_and_save_ips(target_urls)
