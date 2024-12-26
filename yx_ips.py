from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from ipwhois import IPWhois
import time

def get_ip_country(ip):
    """
    使用 IPWhois 查询 IP 的国家简称
    """
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', 'Unknown')
        return country if country else 'Unknown'
    except Exception as e:
        print(f"查询 {ip} 的国家代码失败: {e}")
        return 'Unknown'

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址（使用 Selenium 获取动态加载的内容）
    """
    try:
        # 配置 WebDriver（假设使用 Chrome）
        driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # 修改为您的 chromedriver 路径
        driver.get(url)
        
        # 等待页面加载，确保动态内容加载完毕
        time.sleep(5)  # 可以调整等待时间
        
        # 获取网页的源代码
        page_source = driver.page_source
        driver.quit()

        # 使用正则表达式提取 IP 地址
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', page_source)
        if not ip_addresses:
            print(f"未从 {url} 提取到任何 IP 地址")
        return ip_addresses
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def save_ips_to_file(ips):
    """
    将 IP 地址和其对应的国家信息保存到 ip.txt 文件中
    格式为 IP#国家简称
    """
    ip_with_country = {}

    # 查询每个 IP 地址的国家简称
    for ip in ips:
        country = get_ip_country(ip)
        ip_with_country[ip] = country

    # 保存结果到文件
    with open('ip.txt', 'w') as file:
        for ip, country in sorted(ip_with_country.items()):  # 按 IP 排序
            file.write(f"{ip}#{country}\n")

    print(f"IP 地址已保存到 ip.txt，总计 {len(ip_with_country)} 个 IP 地址")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存
    """
    all_ips = set()
    for url in urls:
        ips = extract_ips_from_web(url)
        all_ips.update(ips)

    # 过滤有效 IP 地址并保存
    valid_ips = [ip for ip in all_ips if re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)]
    save_ips_to_file(valid_ips)

if __name__ == '__main__':
    # 提供要抓取 IP 地址的 URL 列表
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',  # 你可以添加更多目标 URL
    ]
    
    # 执行抓取和保存操作
    fetch_and_save_ips(target_urls)
