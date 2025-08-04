import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

def get_exchange_rate(
    api_key: str,
    from_coin: str = 'USD',
    to_coin: str = 'CNY',
    amount: float = 1
) -> Optional[float]:
    """获取货币兑换汇率
    
    参数:
        api_key: 天行API密钥
        from_coin: 源货币代码(默认USD)
        to_coin: 目标货币代码(默认CNY)
        amount: 兑换金额(默认1)
    
    返回:
        兑换后的金额(失败返回None)
    """
    url = 'https://apis.tianapi.com/fxrate/index'
    params = {
        'key': api_key,
        'fromcoin': from_coin,
        'tocoin': to_coin,
        'money': amount
    }

    try:
        response = requests.post(url, data=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 200:
            return float(data['result']['money'])
        print(f"API错误: {data.get('msg', '未知错误')}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return None
    except (ValueError, KeyError) as e:
        print(f"数据解析错误: {str(e)}")
        return None
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API 地址
#FETCH_URL = "https://crypto-api-vqm0.onrender.com/btc-prices"
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0060472f-9759-40d1-8c57-560f9acfeb21"
#F2_URL = "https://crypto-api-vqm0.onrender.com/fear-greed"

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


def generate_markdown(fg):
    # 获取当前时间并转换为北京时间(UTC+8)
    utc_now = datetime.utcnow()
    bj_now = utc_now + timedelta(hours=8)  # 转换为北京时间
    # 创建Markdown内容，并用实际价格替换占位符
    api_key = "69911d85-9f5e-4823-98f6-d119908b9120"  # 替换为实际API密钥
    fetcher = CryptoPriceFetcher(api_key)
    prices = fetcher.fetch_prices()
    pall = ""
    if 'error' in prices:
        print(f"错误: {prices['error']}")
    else:
        for coin, price in prices.items():
            pall +=("{coin.upper()}: ${price}")

    markdown_content = (
        "## 当前市场汇率:" +fg+"\n"+
        "## 当前市场价格概览\n" +pall+"\n" +
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
    result = get_exchange_rate('8fcbeff2ee50578c4219fdef198ab44f')
    if result:
        fg = (f"当前汇率: 1 USD = {result:.2f} CNY")
    else:
        fg = "汇率查询失败"
    if fg:
        markdown_msg = generate_markdown(fg)
        success = send_wechat_message(webhook_url, markdown_msg)
        if success:
            logger.info("任务执行成功！")
        else:
            logger.error("任务执行失败：POST 失败")
    else:
        logger.error("任务执行失败：获取数据失败")

if __name__ == "__main__":
    main()
