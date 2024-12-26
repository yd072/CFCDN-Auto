from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

def extract_ips_from_web(url):
    """
    使用 Selenium 获取网页内容并提取所有 IP 地址
    """
    try:
        # 设置 Chrome 配置，避免打开浏览器窗口
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
        chrome_options.add_argument("--disable-gpu")  # 禁用 GPU，加速渲染
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # 模拟真实浏览器请求头
        
        # 启动 Chrome 浏览器（使用 webdriver_manager 自动管理 chromedriver）
        print("启动浏览器...")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        
        # 获取页面
        print(f"访问页面: {url}")
        driver.get(url)

        # 等待页面加载完成，直到页面的某个元素出现
        print("等待页面加载...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 获取页面的 HTML 内容
        page_source = driver.page_source
        print("页面加载完成，开始提取 IP 地址...")

        # 解析页面
        ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', page_source)

        if not ip_addresses:
            print(f"未从 {url} 提取到任何 IP 地址")
        
        # 关闭浏览器
        driver.quit()
        
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
