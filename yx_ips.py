from ipwhois import IPWhois
import requests

def get_ip_country(ip):
    """根据 IP 获取国家代码"""
    try:
        # 使用 ipwhois 获取 IP 国家信息
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('country', 'Unknown')  # 如果没有找到国家代码，则返回 'Unknown'
        return country
    except Exception as e:
        print(f"查询 {ip} 时出错: {e}")
        return 'Unknown'

def fetch_ips():
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://cf.090227.xyz',  # 其他目标 URL
    ]

    # 读取已存在的 IP 地址并去重
    existing_ips = set()
    if os.path.exists('ip.txt'):
        with open('ip.txt', 'r') as file:
            existing_ips = set(line.strip().split('#')[0] for line in file)

    new_ips = set()

    for url in target_urls:
        print(f"正在抓取 {url} 的 IP 地址...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取所有 IP 地址（根据具体网站修改选择器）
            ips = set(soup.find_all(text=lambda text: text and is_valid_ip(text)))

            # 将抓取到的 IP 加入新 IP 集合
            new_ips.update(ips)
            print(f"成功从 {url} 抓取到 {len(ips)} 个 IP 地址")
        except Exception as e:
            print(f"抓取 {url} 时发生错误: {e}")

    # 获取 IP 对应的国家简称
    ip_with_country = {}
    for ip in new_ips:
        country = get_ip_country(ip)
        ip_with_country[ip] = country
        print(f"IP: {ip} -> 国家: {country}")

    # 将新的 IP 地址去重并写入文件
    all_ips = existing_ips.union(ip_with_country.keys())  # 合并已存在的和新的 IP 地址
    with open('ip.txt', 'w') as file:
        for ip in sorted(all_ips):  # 按字母顺序排序
            # 输出格式：IP#国家简称（没有空格）
            file.write(f"{ip}#{ip_with_country.get(ip, 'Unknown')}\n")

    print(f"新 IP 已保存到 ip.txt，总计新增 {len(new_ips)} 个 IP 地址")

def is_valid_ip(ip):
    """简单验证 IPv4 地址的正则"""
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip)

if __name__ == '__main__':
    fetch_ips()
