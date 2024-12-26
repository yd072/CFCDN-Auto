import requests
import base64
from datetime import datetime, timedelta
import argparse

# 配置 Fofa API 信息
FOFA_EMAIL = "ozyguv@mailto.plus"  # 替换为你的邮箱
FOFA_API_KEY = "05f9b819fbe15a6652cbdee5564b2ab4"  # 替换为你的 API Key
RESULT_COUNT = 100  # 获取结果的数量

def generate_query(base_query, days=None):
    """生成带时间限制的查询语句"""
    if days and days > 0:
        date_after = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return f'{base_query} && after="{date_after}"'
    return base_query

def fofa_search(email, api_key, query, size):
    """调用 Fofa API 搜索"""
    query_base64 = base64.b64encode(query.encode()).decode()
    url = f"https://fofa.info/api/v1/search/all?email={email}&key={api_key}&qbase64={query_base64}&size={size}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("error"):
            print("Error:", data.get("errmsg"))
            return []
        return data["results"]  # 返回完整结果
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return []

def save_to_file(results, filename):
    """保存结果到文件"""
    try:
        with open(filename, "w") as file:
            for result in results:
                ip = result[0]  # IP 是第一个字段
                country = result[-2]  # 国家简称通常是倒数第二个字段
                file.write(f"{ip}#{country}\n")
        print(f"结果已保存到 {filename}")
    except Exception as e:
        print("保存文件时出错:", e)

if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="Fofa 搜索脚本")
    parser.add_argument(
        "--query", 
        type=str, 
        required=True, 
        help="自定义搜索语句，例如 domain='example.com'"
    )
    parser.add_argument(
        "--days", 
        type=int, 
        default=30, 
        help="时间范围，单位为天（默认：最近 30 天）"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="ip.txt", 
        help="输出文件名（默认：ip.txt）"
    )
    args = parser.parse_args()

    # 生成查询语句
    query = generate_query(args.query, args.days)
    print(f"查询语句: {query}")
    
    # 调用 Fofa API 获取搜索结果
    results = fofa_search(FOFA_EMAIL, FOFA_API_KEY, query, RESULT_COUNT)
    if results:
        save_to_file(results, args.output)
    else:
        print("未找到相关结果或请求失败。")
