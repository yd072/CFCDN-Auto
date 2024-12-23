#!/bin/bash

# 设置语言
export LANG=zh_CN.UTF-8

# 配置目录
BASE_DIR=$(pwd)
FDIP_DIR="${BASE_DIR}/FDIP"
CFST_DIR="${BASE_DIR}/CloudflareST"
URL="https://spurl.api.030101.xyz/50mb"
GF_IP_PATH="${FDIP_DIR}/gf-ip.txt"
GFCS_PATH="${CFST_DIR}/gfcs.txt"

# 创建所需目录
mkdir -p "${FDIP_DIR}"
mkdir -p "${CFST_DIR}"

# 检查测速文件是否存在
if [ ! -f "${GF_IP_PATH}" ]; then
    echo "文件 ${GF_IP_PATH} 不存在，脚本终止。"
    exit 1
fi

# 下载 CloudflareST 工具
echo "=========================下载和解压CloudflareST=========================="
if [ ! -f "${CFST_DIR}/CloudflareST" ]; then
    echo "CloudflareST文件不存在，开始下载..."
    wget -O "${CFST_DIR}/CloudflareST_linux_amd64.tar.gz" https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.5/CloudflareST_linux_amd64.tar.gz
    tar -xzf "${CFST_DIR}/CloudflareST_linux_amd64.tar.gz" -C "${CFST_DIR}"
    chmod +x "${CFST_DIR}/CloudflareST"
else
    echo "CloudflareST文件已存在，跳过下载步骤。"
fi

# 使用 CloudflareST 对 gf-ip.txt 文件中的 IP 进行测速
echo "======================运行 CloudflareSpeedTest ========================="
"${CFST_DIR}/CloudflareST" -tp 443 -f "${GF_IP_PATH}" -n 500 -dn 5 -tl 250 -tll 10 -o "${CFST_DIR}/gf.csv" -url "$URL"

# 筛选测速结果中下载速度大于 10mb/s 的 IP，并保存到 gfcs.txt
echo "==================筛选下载速度高于 10mb/s 的IP地址并去重===================="
awk -F, '!seen[$1]++' "${CFST_DIR}/gf.csv" | awk -F, 'NR>1 && $6 > 10 {print $1 "#" $6 "mb/s"}' > "${GFCS_PATH}"

# 提示脚本完成
echo "===============================脚本执行完成==============================="
echo "测速完成，高速 IP 地址保存在：${GFCS_PATH}"
