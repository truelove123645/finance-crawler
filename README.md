# 📊 金融市场数据爬虫

一键获取全球金融市场最新行情，生成精美HTML报表。

## 支持的市场

| 市场 | 数据源 | 内容 |
|------|--------|------|
| 🇨🇳 A股 | akshare | 大盘指数、热门股票 |
| 🇺🇸 美股 | yfinance | 热门科技股 |
| ₿ 加密货币 | CoinGecko | BTC、ETH等主流币 |
| 📊 基金 | akshare | 热门基金净值 |
| 💱 外汇 | ExchangeRate-API | 主要货币对 |
| 📰 新闻 | 新浪财经 | 最新财经新闻 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

```bash
python main.py
```

### 3. 查看报表

运行完成后，在 `reports` 目录下会生成：
- `finance_report_latest.html` - 最新报表（每次运行覆盖）
- `finance_report_时间戳.html` - 历史报表

用浏览器打开 `finance_report_latest.html` 即可查看。

## 自定义配置

在 `main.py` 文件顶部的配置区域，可以修改：

```python
# A股指数和热门股票
A_STOCK_INDICES = ["sh000001", "sz399001", "sz399006"]
A_STOCK_HOT = ["600519", "000858", "601318", "600036", "000333"]

# 美股热门股票
US_STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "TSLA", "META"]

# 加密货币
CRYPTO_COINS = ["bitcoin", "ethereum", "binancecoin", "solana", "ripple", "cardano"]

# 基金代码
FUND_CODES = ["161725", "161726", "005827", "003834", "110011"]

# 外汇货币对
FX_PAIRS = ["USD/CNY", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
```

## 报表特性

- 🎨 精美的暗色主题设计
- 📱 响应式布局，支持手机查看
- 🟢🟢 涨跌颜色标识（绿色涨、红色跌）
- 📰 财经新闻滚动展示

## 常见问题

### Q: 部分数据获取失败？
A: 可能是网络限制或API限流，脚本会自动跳过失败的数据源，其他数据正常获取。

### Q: 想添加更多股票？
A: 修改 `main.py` 中的 `A_STOCK_HOT` 或 `US_STOCKS` 列表，添加股票代码即可。

### Q: 如何定时运行？
A: 可以使用 Windows 任务计划程序或 Linux cron 定时执行 `python main.py`。

## 依赖说明

- `akshare` - A股和基金数据
- `yfinance` - 美股数据
- `requests` - HTTP请求
- `pandas` - 数据处理
- `tabulate` - 表格展示
- `jinja2` - HTML模板渲染

## 免责声明

⚠️ 本工具仅供学习和参考，数据来源第三方API，不保证实时性和准确性。投资有风险，决策需谨慎。

---

Made with ❤️
