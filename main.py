#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融市场数据爬虫 - 获取最新市场行情
支持：A股、美股、基金、加密货币、外汇、财经新闻
"""

import akshare as ak
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
import json
import os
import sys

# Windows编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================
# 配置区域 - 可自定义修改
# ============================================================

# A股指数和热门股票
A_STOCK_INDICES = ["sh000001", "sz399001", "sz399006"]  # 上证指数、深证成指、创业板指
A_STOCK_HOT = ["600519", "000858", "601318", "600036", "000333"]  # 贵州茅台、五粮液、平安、招商银行、美的

# 美股热门股票
US_STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "TSLA", "META"]

# 加密货币（CoinGecko ID）
CRYPTO_COINS = ["bitcoin", "ethereum", "binancecoin", "solana", "ripple", "cardano"]

# 基金代码（热门基金）
FUND_CODES = ["161725", "161726", "005827", "003834", "110011"]

# 外汇货币对
FX_PAIRS = ["USD/CNY", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]

# ============================================================
# 数据获取函数
# ============================================================

def get_a_stock_data():
    """获取A股市场数据"""
    print("\n📈 正在获取A股数据...")
    results = {
        "indices": [],
        "hot_stocks": []
    }

    try:
        # 获取大盘指数
        for code in A_STOCK_INDICES:
            try:
                df = ak.stock_zh_index_spot_em()
                row = df[df['代码'] == code]
                if not row.empty:
                    results["indices"].append({
                        "名称": row.iloc[0]['名称'],
                        "最新价": row.iloc[0]['最新价'],
                        "涨跌幅": f"{row.iloc[0]['涨跌幅']:.2f}%",
                        "涨跌额": row.iloc[0]['涨跌额'],
                        "成交量": row.iloc[0]['成交量'],
                        "成交额": row.iloc[0]['成交额']
                    })
            except Exception as e:
                print(f"  获取指数 {code} 失败: {e}")

        # 获取热门股票
        for code in A_STOCK_HOT:
            try:
                df = ak.stock_zh_a_spot_em()
                row = df[df['代码'] == code]
                if not row.empty:
                    results["hot_stocks"].append({
                        "代码": code,
                        "名称": row.iloc[0]['名称'],
                        "最新价": row.iloc[0]['最新价'],
                        "涨跌幅": f"{row.iloc[0]['涨跌幅']:.2f}%",
                        "成交量(手)": row.iloc[0]['成交量'],
                        "成交额(万)": row.iloc[0]['成交额'] / 10000
                    })
            except Exception as e:
                print(f"  获取股票 {code} 失败: {e}")

    except Exception as e:
        print(f"  A股数据获取失败: {e}")

    return results


def get_us_stock_data():
    """获取美股市场数据"""
    print("\n🇺🇸 正在获取美股数据...")
    results = []

    for symbol in US_STOCKS:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d")

            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0

                results.append({
                    "代码": symbol,
                    "名称": info.get('shortName', symbol),
                    "最新价": f"${current_price:.2f}",
                    "涨跌幅": f"{change_pct:+.2f}%",
                    "涨跌额": f"${change:+.2f}",
                    "成交量": hist['Volume'].iloc[-1]
                })
        except Exception as e:
            print(f"  获取美股 {symbol} 失败: {e}")

    return results


def get_crypto_data():
    """获取加密货币数据"""
    print("\n₿ 正在获取加密货币数据...")
    results = []

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ",".join(CRYPTO_COINS),
            "order": "market_cap_desc",
            "sparkline": "false",
            "price_change_percentage": "24h,7d"
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for coin in data:
                results.append({
                    "名称": coin['name'],
                    "代码": coin['symbol'].upper(),
                    "价格(USD)": f"${coin['current_price']:,.2f}",
                    "24h涨跌": f"{coin['price_change_percentage_24h']:+.2f}%" if coin['price_change_percentage_24h'] else "N/A",
                    "7d涨跌": f"{coin['price_change_percentage_7d_in_currency']:+.2f}%" if coin.get('price_change_percentage_7d_in_currency') else "N/A",
                    "市值(亿)": f"${coin['market_cap']/1e8:,.0f}",
                    "24h成交量(亿)": f"${coin['total_volume']/1e8:,.0f}"
                })
        else:
            print(f"  CoinGecko API返回状态码: {response.status_code}")

    except Exception as e:
        print(f"  加密货币数据获取失败: {e}")

    return results


def get_fund_data():
    """获取基金数据"""
    print("\n📊 正在获取基金数据...")
    results = []

    for code in FUND_CODES:
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if not df.empty:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                change = ((latest['单位净值'] - prev['单位净值']) / prev['单位净值']) * 100

                results.append({
                    "基金代码": code,
                    "最新净值": f"{latest['单位净值']:.4f}",
                    "涨跌幅": f"{change:+.2f}%",
                    "净值日期": str(latest['净值日期'])[:10]
                })
        except Exception as e:
            print(f"  获取基金 {code} 失败: {e}")

    return results


def get_forex_data():
    """获取外汇数据"""
    print("\n💱 正在获取外汇数据...")
    results = []

    try:
        # 使用akshare获取外汇数据
        df = ak.fx_spot_quote()
        if not df.empty:
            for pair in FX_PAIRS:
                # akshare的外汇数据格式可能不同，需要适配
                # 这里使用备用方案：exchangerate-api
                base, quote = pair.split("/")
                url = f"https://api.exchangerate-api.com/v4/latest/{base}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rate = data['rates'].get(quote, 0)
                    results.append({
                        "货币对": pair,
                        "汇率": f"{rate:.4f}",
                        "更新时间": data.get('date', 'N/A')
                    })
    except Exception as e:
        print(f"  外汇数据获取失败，使用备用方案...")
        # 备用方案
        for pair in FX_PAIRS:
            try:
                base, quote = pair.split("/")
                url = f"https://api.exchangerate-api.com/v4/latest/{base}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rate = data['rates'].get(quote, 0)
                    results.append({
                        "货币对": pair,
                        "汇率": f"{rate:.4f}",
                        "更新时间": data.get('date', 'N/A')
                    })
            except Exception as e2:
                print(f"  获取外汇 {pair} 失败: {e2}")

    return results


def get_finance_news():
    """获取财经新闻"""
    print("\n📰 正在获取财经新闻...")
    results = []

    try:
        # 使用新浪财经获取新闻
        url = "https://feed.mix.sina.com.cn/api/roll/get"
        params = {
            "pageid": "153",
            "lid": "2516",
            "k": "",
            "num": 10,
            "page": 1
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('result') and data['result'].get('data'):
                for item in data['result']['data'][:10]:
                    results.append({
                        "标题": item.get('title', 'N/A'),
                        "来源": item.get('media_name', 'N/A'),
                        "时间": datetime.fromtimestamp(int(item.get('ctime', 0))).strftime('%Y-%m-%d %H:%M') if item.get('ctime') else 'N/A'
                    })
    except Exception as e:
        print(f"  财经新闻获取失败: {e}")

    # 备用：如果新浪失败，尝试东方财富
    if not results:
        try:
            df = ak.stock_info_global_em()
            if not df.empty:
                for _, row in df.head(10).iterrows():
                    results.append({
                        "标题": row.get('标题', 'N/A'),
                        "来源": "东方财富",
                        "时间": str(row.get('发布时间', 'N/A'))[:16]
                    })
        except Exception as e:
            print(f"  备用新闻源也失败: {e}")

    return results


# ============================================================
# 报表生成函数
# ============================================================

def generate_html_report(data, output_path):
    """生成HTML报表"""
    print("\n📄 正在生成HTML报表...")

    html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金融市场数据报表</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .timestamp {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .section h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }
        .emoji { font-size: 1.2em; margin-right: 10px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th {
            background: rgba(255,255,255,0.1);
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        tr:hover { background: rgba(255,255,255,0.05); }
        .positive { color: #00ff88; }
        .negative { color: #ff4757; }
        .news-item {
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .news-title { font-size: 1em; margin-bottom: 5px; }
        .news-meta { color: #888; font-size: 0.85em; }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            table { font-size: 0.85em; }
            th, td { padding: 8px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 金融市场数据报表</h1>
        <p class="timestamp">生成时间：{{ timestamp }}</p>

        {% if data.a_stock.indices %}
        <div class="section">
            <h2><span class="emoji">🇨🇳</span>A股大盘指数</h2>
            <table>
                <tr>
                    <th>指数名称</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>涨跌额</th>
                    <th>成交量</th>
                    <th>成交额</th>
                </tr>
                {% for item in data.a_stock.indices %}
                <tr>
                    <td>{{ item['名称'] }}</td>
                    <td>{{ item['最新价'] }}</td>
                    <td class="{{ 'positive' if '+' in item['涨跌幅'] else 'negative' }}">{{ item['涨跌幅'] }}</td>
                    <td>{{ item['涨跌额'] }}</td>
                    <td>{{ item['成交量'] }}</td>
                    <td>{{ item['成交额'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if data.a_stock.hot_stocks %}
        <div class="section">
            <h2><span class="emoji">🔥</span>A股热门股票</h2>
            <table>
                <tr>
                    <th>代码</th>
                    <th>名称</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>成交量(手)</th>
                    <th>成交额(万)</th>
                </tr>
                {% for item in data.a_stock.hot_stocks %}
                <tr>
                    <td>{{ item['代码'] }}</td>
                    <td>{{ item['名称'] }}</td>
                    <td>{{ item['最新价'] }}</td>
                    <td class="{{ 'positive' if '+' in item['涨跌幅'] else 'negative' }}">{{ item['涨跌幅'] }}</td>
                    <td>{{ item['成交量(手)'] }}</td>
                    <td>{{ "%.2f"|format(item['成交额(万)']) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if data.us_stocks %}
        <div class="section">
            <h2><span class="emoji">🇺🇸</span>美股热门股票</h2>
            <table>
                <tr>
                    <th>代码</th>
                    <th>名称</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>涨跌额</th>
                    <th>成交量</th>
                </tr>
                {% for item in data.us_stocks %}
                <tr>
                    <td>{{ item['代码'] }}</td>
                    <td>{{ item['名称'] }}</td>
                    <td>{{ item['最新价'] }}</td>
                    <td class="{{ 'positive' if '+' in item['涨跌幅'] else 'negative' }}">{{ item['涨跌幅'] }}</td>
                    <td>{{ item['涨跌额'] }}</td>
                    <td>{{ item['成交量'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if data.crypto %}
        <div class="section">
            <h2><span class="emoji">₿</span>加密货币</h2>
            <table>
                <tr>
                    <th>名称</th>
                    <th>代码</th>
                    <th>价格(USD)</th>
                    <th>24h涨跌</th>
                    <th>7d涨跌</th>
                    <th>市值(亿)</th>
                    <th>24h成交量(亿)</th>
                </tr>
                {% for item in data.crypto %}
                <tr>
                    <td>{{ item['名称'] }}</td>
                    <td>{{ item['代码'] }}</td>
                    <td>{{ item['价格(USD)'] }}</td>
                    <td class="{{ 'positive' if '+' in item['24h涨跌'] else 'negative' }}">{{ item['24h涨跌'] }}</td>
                    <td class="{{ 'positive' if '+' in item['7d涨跌'] else 'negative' }}">{{ item['7d涨跌'] }}</td>
                    <td>{{ item['市值(亿)'] }}</td>
                    <td>{{ item['24h成交量(亿)'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if data.funds %}
        <div class="section">
            <h2><span class="emoji">📊</span>基金净值</h2>
            <table>
                <tr>
                    <th>基金代码</th>
                    <th>最新净值</th>
                    <th>涨跌幅</th>
                    <th>净值日期</th>
                </tr>
                {% for item in data.funds %}
                <tr>
                    <td>{{ item['基金代码'] }}</td>
                    <td>{{ item['最新净值'] }}</td>
                    <td class="{{ 'positive' if '+' in item['涨跌幅'] else 'negative' }}">{{ item['涨跌幅'] }}</td>
                    <td>{{ item['净值日期'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if data.forex %}
        <div class="section">
            <h2><span class="emoji">💱</span>外汇汇率</h2>
            <table>
                <tr>
                    <th>货币对</th>
                    <th>汇率</th>
                    <th>更新时间</th>
                </tr>
                {% for item in data.forex %}
                <tr>
                    <td>{{ item['货币对'] }}</td>
                    <td>{{ item['汇率'] }}</td>
                    <td>{{ item['更新时间'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if data.news %}
        <div class="section">
            <h2><span class="emoji">📰</span>最新财经新闻</h2>
            {% for item in data.news %}
            <div class="news-item">
                <div class="news-title">{{ item['标题'] }}</div>
                <div class="news-meta">{{ item['来源'] }} · {{ item['时间'] }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="footer">
            <p>数据来源：新浪财经、Yahoo Finance、CoinGecko、ExchangeRate-API</p>
            <p>⚠️ 数据仅供参考，投资需谨慎</p>
        </div>
    </div>
</body>
</html>
    """

    from jinja2 import Template
    template = Template(html_template)

    html_content = template.render(
        data=data,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"  ✅ HTML报表已生成: {output_path}")


def print_console_summary(data):
    """在控制台打印摘要"""
    print("\n" + "=" * 60)
    print("📊 金融市场数据摘要")
    print("=" * 60)

    # A股指数
    if data['a_stock']['indices']:
        print("\n🇨🇳 A股大盘指数:")
        for idx in data['a_stock']['indices']:
            print(f"  {idx['名称']}: {idx['最新价']}  {idx['涨跌幅']}")

    # A股热门
    if data['a_stock']['hot_stocks']:
        print("\n🔥 A股热门股票:")
        for stock in data['a_stock']['hot_stocks'][:3]:
            print(f"  {stock['名称']}({stock['代码']}): {stock['最新价']}  {stock['涨跌幅']}")

    # 美股
    if data['us_stocks']:
        print("\n🇺🇸 美股热门:")
        for stock in data['us_stocks'][:3]:
            print(f"  {stock['名称']}({stock['代码']}): {stock['最新价']}  {stock['涨跌幅']}")

    # 加密货币
    if data['crypto']:
        print("\n₿ 加密货币:")
        for coin in data['crypto'][:3]:
            print(f"  {coin['名称']}: {coin['价格(USD)']}  {coin['24h涨跌']}")

    # 外汇
    if data['forex']:
        print("\n💱 主要汇率:")
        for fx in data['forex'][:3]:
            print(f"  {fx['货币对']}: {fx['汇率']}")

    # 新闻
    if data['news']:
        print("\n📰 最新新闻:")
        for news in data['news'][:3]:
            print(f"  • {news['标题']}")

    print("\n" + "=" * 60)


# ============================================================
# 主程序
# ============================================================

def main():
    """主函数"""
    print("=" * 60)
    print("🏦 金融市场数据爬虫 v1.0")
    print("=" * 60)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)

    # 收集所有数据
    all_data = {
        "a_stock": {
            "indices": [],
            "hot_stocks": []
        },
        "us_stocks": [],
        "crypto": [],
        "funds": [],
        "forex": [],
        "news": []
    }

    # 获取各类数据
    try:
        a_stock_data = get_a_stock_data()
        all_data["a_stock"] = a_stock_data
    except Exception as e:
        print(f"❌ A股数据获取失败: {e}")

    try:
        all_data["us_stocks"] = get_us_stock_data()
    except Exception as e:
        print(f"❌ 美股数据获取失败: {e}")

    try:
        all_data["crypto"] = get_crypto_data()
    except Exception as e:
        print(f"❌ 加密货币数据获取失败: {e}")

    try:
        all_data["funds"] = get_fund_data()
    except Exception as e:
        print(f"❌ 基金数据获取失败: {e}")

    try:
        all_data["forex"] = get_forex_data()
    except Exception as e:
        print(f"❌ 外汇数据获取失败: {e}")

    try:
        all_data["news"] = get_finance_news()
    except Exception as e:
        print(f"❌ 财经新闻获取失败: {e}")

    # 打印控制台摘要
    print_console_summary(all_data)

    # 生成HTML报表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(output_dir, f"finance_report_{timestamp}.html")
    generate_html_report(all_data, html_path)

    # 同时保存一份最新的报表（覆盖）
    latest_path = os.path.join(output_dir, "finance_report_latest.html")
    generate_html_report(all_data, latest_path)

    print(f"\n✅ 数据获取完成！")
    print(f"📁 报表保存位置: {output_dir}")
    print(f"📄 最新报表: {latest_path}")

    return all_data


if __name__ == "__main__":
    main()
