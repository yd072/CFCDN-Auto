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

# 筛选下载速度高于 10mb/s 的 IP地址并去重
echo "==================筛选下载速度高于 10mb/s 的IP地址并去重===================="
awk -F, 'NR>1 && $6 > 10 && !seen[$1]++ {print $1 "#" $6 "mb/s"}' "${CFST_DIR}/ip.csv" > "${CFST_DIR}/gfip.txt" || { echo "筛选 IP 失败！"; exit 1; }

echo "===============================脚本执行完成==============================="
