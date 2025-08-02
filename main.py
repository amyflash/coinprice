import requests
import time
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API 地址
FETCH_URL = "https://crypto-api-vqm0.onrender.com/btc-prices"
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0060472f-9759-40d1-8c57-560f9acfeb21"
F2_URL = "https://crypto-api-vqm0.onrender.com/fear-greed"

def fetch_prices():
    try:
        logger.info(f"正在从 {FETCH_URL} 获取价格数据...")
        response = requests.get(FETCH_URL, timeout=10)
        response.raise_for_status()  # 检查 HTTP 错误
        data = response.json()
        logger.info(f"成功获取数据: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None
    except ValueError as e:
        logger.error(f"JSON 解析失败: {e}")
        return None
        
def fetch_fg():
    try:
        logger.info(f"正在从 {F2_URL} 获取价格数据...")
        response = requests.get(F2_URL, timeout=10)
        response.raise_for_status()  # 检查 HTTP 错误
        data = response.json()
        logger.info(f"成功获取数据: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None
    except ValueError as e:
        logger.error(f"JSON 解析失败: {e}")
        return None


def generate_markdown(prices,fg):
    # 获取当前时间并转换为北京时间(UTC+8)
    utc_now = datetime.utcnow()
    bj_now = utc_now + timedelta(hours=8)  # 转换为北京时间
    # 创建Markdown内容，并用实际价格替换占位符
    markdown_content = (
        "## 当前市场恐惧贪婪指数:" +fg+"\n"+
        "## 当前市场btc价格概览\n" +
        "| 交易所 | 价格 (USDT) |\n" +
        "| --- | ---: |\n" +
        f"| OKX | ${prices['okx']} |\n" +
       "\n*数据更新时间: {}*".format(bj_now.strftime("%Y-%m-%d %H:%M 北京时间"))
    )
    
    return markdown_content

def send_wechat_message(webhook_url, markdown_content):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content
        }
    }
    response = requests.post(webhook_url, json=data, headers=headers)
    if response.status_code == 200:
        print("消息发送成功")
        return 1
    else:
        print(f"消息发送失败: {response.text}")
        return 0

# 使用示例
def main():
    logger.info("任务开始执行...")
    prices = fetch_prices()
    fg = fetch_fg()
    if prices:
        markdown_msg = generate_markdown(prices,fg)
        success = send_wechat_message(webhook_url, markdown_msg)
        if success:
            logger.info("任务执行成功！")
        else:
            logger.error("任务执行失败：POST 失败")
    else:
        logger.error("任务执行失败：获取数据失败")

if __name__ == "__main__":
    main()
