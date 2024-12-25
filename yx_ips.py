import asyncio
import logging
import re
from pyppeteer import launch

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class StealthReader:
    def __init__(self, target_url):
        self.target_url = target_url
        self.browser = None
        self.page = None

    async def __aenter__(self):
        await self.init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()

    async def init_browser(self):
        logging.info(f"初始化浏览器... 目标网站: {self.target_url}")
        self.browser = await launch({
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--disable-blink-features=AutomationControlled',
                '--disable-gpu',
                '--disable-dev-shm-usage',
            ],
            'ignoreHTTPSErrors': True,
            'defaultViewport': None
        })
        self.page = await self.browser.newPage()

    async def scrape(self):
        """抓取 IP 信息并保存到文件"""
        logging.info(f"开始访问目标网页: {self.target_url}")
        try:
            await self.page.goto(self.target_url, {'waitUntil': 'domcontentloaded'})

            # 等待页面加载完成
            await asyncio.sleep(2)

            logging.info(f"开始提取目标网站的 IP 信息: {self.target_url}")
            # 提取整个页面的 HTML
            page_content = await self.page.content()

            # 使用正则表达式匹配 IP 地址
            ip_match = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', page_content)
            if ip_match:
                logging.info(f"找到的 IP 地址: {ip_match}")

                # 将 IP 保存到文件
                with open("ip.txt", "a") as file:
                    for ip_address in ip_match:
                        file.write(f"{self.target_url} - {ip_address}\n")
                logging.info(f"目标网站的 IP 地址已保存到 ip.txt 文件")
            else:
                logging.info(f"未找到符合格式的 IP 地址: {self.target_url}")
        except Exception as e:
            logging.error(f"提取 IP 地址时出错: {e}")

    async def run(self):
        """主程序入口"""
        await self.scrape()

async def main():
    # 定义多个目标网站
    target_urls = [
        'https://stock.hostmonit.com/CloudFlareYes',
        'https://example.com',
        'https://another-example.com'
    ]

    # 遍历所有目标网站
    for url in target_urls:
        async with StealthReader(url) as reader:
            await reader.run()

if __name__ == "__main__":
    asyncio.run(main())
