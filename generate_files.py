import requests
import re
import eventlet

# 目标 URL 列表
urls = [
    "http://36.249.150.1:9901",
"http://36.249.151.1:9901",
"http://36.40.236.1:9999",
"http://36.44.157.1:9901",
"http://36.99.206.1:9901",
"http://47.104.163.1:9901",
"http://47.116.70.1:9901",
"http://49.232.48.1:9901",
"http://49.234.31.1:7004",
"http://58.17.116.1:9908",
"http://58.19.244.1:1111",
"http://58.209.101.1:9901",
"http://58.216.229.1:9901",
"http://58.220.219.1:9901",
"http://58.23.27.1:9901",
"http://58.243.224.1:9901",
"http://58.243.93.1:9901",
"http://58.48.37.1:1111",
"http://58.48.5.1:1111",
"http://59.173.183.1:9901",
"http://59.63.22.1:8888",
"http://60.169.254.1:9901",
"http://60.172.59.1:9901",
"http://60.174.86.1:9901",
"http://61.136.172.1:9901",
"http://61.136.67.1:50085",
"http://61.156.228.1:8154",
"http://61.173.144.1:9901"
    # 其他URL略...
]

# 修改 URL 生成子网范围的所有地址
def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)
    return modified_urls

# 检查 URL 是否有效
def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except:
        pass
    return None

# 获取可用 URL
valid_urls = []
for url in urls:
    for modified_url in modify_urls(url):
        if is_url_accessible(modified_url):
            valid_urls.append(modified_url)

# 提取频道
results = []
for url in valid_urls:
    try:
        response = requests.get(url, timeout=0.5)
        json_data = response.json()
        for item in json_data.get('data', []):
            if isinstance(item, dict):
                name = item.get('name')
                urlx = item.get('url')
                if urlx and not urlx.startswith("http"):
                    base_url = url.split('/')[2]
                    urlx = f"http://{base_url}{urlx}"
                if name and urlx:
                    name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                    results.append(f"{name},{urlx}")
    except:
        continue

# 保存 M3U 文件
with open("itvlist.m3u", 'w', encoding='utf-8') as m3u_file:
    m3u_file.write('#EXTM3U\n')
    for result in results:
        name, url = result.split(',')
        m3u_file.write(f"#EXTINF:-1,{name}\n{url}\n")

# 保存 TXT 文件
with open("results.txt", 'w', encoding='utf-8') as txt_file:
    for result in results:
        txt_file.write(f"{result}\n")
