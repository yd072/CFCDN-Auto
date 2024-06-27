import requests
import os
import logging

# 配置
CF_API_KEY = os.getenv('CF_API_KEY')
CF_ZONE_YID = os.getenv('CF_ZONE_YID')
CF_DNS_NAME = os.getenv('CF_DNS_NAME')
FILE_PATH = 'sgfd_ips.txt'
SGCS_FILE_PATH = 'CloudflareST/sgcs.txt'
IPINFO_API = '568895973bafba'

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 第一步：从URL和本地文件获取IP数据
def get_ip_data():
    url1 = 'https://raw.githubusercontent.com/ymyuuu/IPDB/main/bestproxy.txt'

    try:
        response1 = requests.get(url1)
        response1.raise_for_status()  # 检查请求是否成功
        ip_list1 = response1.text.splitlines()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from {url1}: {e}")
        ip_list1 = []

    # 从本地文件获取IP数据
    ip_list2 = []
    if os.path.exists(SGCS_FILE_PATH):
        try:
            with open(SGCS_FILE_PATH, 'r') as f:
                ip_list2 = f.read().splitlines()
        except IOError as e:
            logger.error(f"Error reading local file {SGCS_FILE_PATH}: {e}")

    # 合并并清洗IP地址列表
    ip_list = ip_list1 + ip_list2
    cleaned_ips = clean_ip_data(ip_list)
    return cleaned_ips

# 新步骤：去除IP地址中的速度信息和验证IP格式
def clean_ip_data(ip_list):
    cleaned_ips = []
    for ip in ip_list:
        ip = ip.split('#')[0]  # 去除速度信息，只保留IP地址
        if is_valid_ip(ip):
            cleaned_ips.append(ip)
    return cleaned_ips

# 校验IP地址格式
def is_valid_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            if not 0 <= int(part) <= 255:
                return False
        except ValueError:
            return False
    return True

# 第二步：通过ipinfo.io查询新加坡IP地址
def filter_and_format_ips(ip_list):
    singapore_ips = []
    for ip in ip_list:
        ip = ip.split('#')[0]  # 再次确保去除速度信息
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/country?token={IPINFO_API}")
            country_code = response.text.strip()
            if country_code == 'SG':
                singapore_ips.append(f"{ip}#SG")
        except Exception as e:
            logger.error(f"Error processing IP {ip}: {e}")
    return singapore_ips

# 新步骤：去除重复的IP地址
def remove_duplicate_ips(ip_addresses):
    seen_ips = set()
    unique_ips = []
    for ip in ip_addresses:
        ip_base = ip.split('#')[0]
        if ip_base not in seen_ips:
            seen_ips.add(ip_base)
            unique_ips.append(ip)
    return unique_ips

# 第三步：将格式化后的新加坡IP地址写入到sgfd_ips.txt文件
def write_to_file(ip_addresses):
    try:
        with open(FILE_PATH, 'w') as f:
            for ip in ip_addresses:
                f.write(ip + '\n')
    except IOError as e:
        logger.error(f"Error writing to file {FILE_PATH}: {e}")

# 第四步：清除指定Cloudflare域名的所有DNS记录
def clear_dns_records():
    if not CF_API_KEY or not CF_ZONE_YID or not CF_DNS_NAME:
        logger.error("Cloudflare API credentials not provided.")
        return

    headers = {
        'Authorization': f'Bearer {CF_API_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        # 获取现有的DNS记录
        dns_records_url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_YID}/dns_records'
        response = requests.get(dns_records_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        dns_records = response.json()

        # 删除旧的DNS记录
        for record in dns_records['result']:
            if record['name'] == CF_DNS_NAME:
                delete_url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_YID}/dns_records/{record["id"]}'
                requests.delete(delete_url, headers=headers)
                logger.info(f"Deleted DNS record {record['name']} with id {record['id']}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error clearing DNS records: {e}")
    except KeyError as e:
        logger.error(f"Error parsing DNS records response: {e}")

# 第五步：更新Cloudflare域名的DNS记录为sgfd_ips.txt文件中的IP地址
def update_dns_records():
    try:
        with open(FILE_PATH, 'r') as f:
            ips_to_update = [line.split('#')[0].strip() for line in f]

        headers = {
            'Authorization': f'Bearer {CF_API_KEY}',
            'Content-Type': 'application/json',
        }

        dns_records_url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_YID}/dns_records'
        for ip in ips_to_update:
            data = {
                'type': 'A',
                'name': CF_DNS_NAME,
                'content': ip,
                'ttl': 60,
                'proxied': False,
            }
            response = requests.post(dns_records_url, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功

            if response.status_code == 200:
                logger.info(f"Successfully updated DNS record for {CF_DNS_NAME} to {ip}")
            else:
                logger.error(f"Failed to update DNS record for {CF_DNS_NAME} to {ip}. Status code: {response.status_code}")
    except IOError as e:
        logger.error(f"Error reading file {FILE_PATH}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating DNS records: {e}")

# 主函数：按顺序执行所有步骤
def main():
    try:
        # 第一步：获取IP数据
        ip_list = get_ip_data()

        # 第二步：过滤并格式化新加坡IP地址
        singapore_ips = filter_and_format_ips(ip_list)

        # 新步骤：去除重复的IP地址
        unique_singapore_ips = remove_duplicate_ips(singapore_ips)

        # 如果没有找到符合条件的新加坡IP，则不执行任何操作
        if not unique_singapore_ips:
            logger.info("No Singapore IPs found. Keeping existing sgfd_ips.txt file.")
            return

        # 第三步：将格式化后的新加坡IP地址写入文件
        write_to_file(unique_singapore_ips)

        # 第四步：清除指定Cloudflare域名的所有DNS记录
        clear_dns_records()

        # 第五步：更新Cloudflare域名的DNS记录为sgfd_ips.txt文件中的IP地址
        update_dns_records()

    finally:
        # 可以在这里添加其他资源的释放操作，如数据库连接等
        pass

if __name__ == "__main__":
    main()
