#!/bin/bash

# 设置语言
export LANG=zh_CN.UTF-8

# 配置目录
BASE_DIR=$(pwd)
CFST_DIR="${BASE_DIR}/CloudflareST"
URL=${1:-"https://spurl.api.030101.xyz/50mb"}

# 创建所需目录
mkdir -p "${CFST_DIR}"

# 下载 CloudflareST 工具
echo "=========================下载和解压 CloudflareST=========================="
if [ ! -f "${CFST_DIR}/CloudflareST" ]; then
    echo "CloudflareST 文件不存在，开始下载..."
    wget -O "${CFST_DIR}/CloudflareST_linux_amd64.tar.gz" https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.5/CloudflareST_linux_amd64.tar.gz || { echo "下载失败！"; exit 1; }
    tar -xzf "${CFST_DIR}/CloudflareST_linux_amd64.tar.gz" -C "${CFST_DIR}" || { echo "解压失败！"; exit 1; }
    chmod +x "${CFST_DIR}/CloudflareST"
else
    echo "CloudflareST 文件已存在，跳过下载步骤。"
fi

# 运行 CloudflareST 进行测速
echo "======================运行 CloudflareSpeedTest ========================="
"${CFST_DIR}/CloudflareST" -tp 443 -f "${CFST_DIR}/ip.txt" -n 500 -dn 5 -tl 200 -tll 10 -o "${CFST_DIR}/ip.csv" -url "$URL" || { echo "测速失败！"; exit 1; }

# 国家简称映射
declare -A country_map
country_map["China"]="CN"
country_map["United States"]="US"
country_map["United Kingdom"]="GB"
country_map["Germany"]="DE"
country_map["France"]="FR"
country_map["India"]="IN"
country_map["Russia"]="RU"
country_map["Australia"]="AU"
# 继续添加其他国家的映射...

# 筛选下载速度高于 10mb/s 的 IP地址并添加国家简称
echo "==================筛选下载速度高于 10mb/s 的IP地址并添加国家简称===================="
awk -F, 'NR>1 && $6 > 10 && !seen[$1]++ { 
    country = $2; 
    if (country_map[country]) {
        print $1 "#" country_map[country]
    } else {
        print $1 "#" country 
    }
}' "${CFST_DIR}/ip.csv" > "${CFST_DIR}/gfip.txt" || { echo "筛选 IP 失败！"; exit 1; }

echo "===============================脚本执行完成==============================="
echo "筛选结果已保存到 ${CFST_DIR}/gfip.txt"
