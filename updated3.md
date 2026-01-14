# Trader 页面 + AI 交易员系统重构 —— 技术设计与实施方案（更新 A股数据源）

> 提示：可以让 AI IDE 检查是否完全实现功能，方法：向 AI 提示指令——
> "请检查当前项目实现是否覆盖以下功能：Trader 页面可输入股票代码、AI 获取历史 K 线数据并判断多头/空头趋势、显示详细逻辑、历史类似走势参考；设置页面可配置交易员和策略性格；前端可视化 K 线、成交量、换手率；Docker 部署与一键启动；以及 AI 输出 JSON 结构。请列出缺失或未完全实现的功能点。"

> 目标：将原有智能筛股平台升级为**单股分析 + AI 交易员 + 可视化 + 历史趋势参考**的工程级系统。用户通过浏览器输入股票代码即可获取分析结果，并可配置交易员策略性格。

---

## 一、数据源更新

* **A股数据**：使用 **efinance** 获取历史 K 线、成交量、换手率和财务指标，保证数据完整性和稳定性。
* **美股数据**：使用 **yfinance** 获取历史行情和财务指标。
* **其他市场（港股/期货等）**：使用 **AkShare**。

### Python 示例

```python
# A股
import efinance as ef
stock_data = ef.stock.get_quote_history('000001')

# 美股
import yfinance as yf
msft = yf.Ticker('MSFT')
hist = msft.history(period="1y")

# 其他市场
import akshare as ak
hk_stock = ak.stock_hk_hist(symbol='00700', period='daily')
```

---

## 二、数据处理

* 对不同来源数据统一格式为 DataFrame
* 包括日期、开盘价、收盘价、最高价、最低价、成交量、换手率
* 提供给 AI 交易员分析与可视化

---

## 三、Trader 页面功能

1. 输入股票代码 → 根据市场类型选择对应数据源
2. K 线可视化（ECharts / TradingView / Plotly）
3. AI 趋势判断

   * 输入：历史 K 线数据 + 交易员策略性格 + 信心度阈值
   * 输出：趋势、多头/空头判断、逻辑说明、历史相似走势、信心度、预期收益率、will_trade

---

## 四、设置页面功能

* 配置交易员 API（模型类型、URL、API Key）
* 配置交易员性格（风险偏好、趋势敏感度、多空偏好、信心阈值）

---

## 五、前端可视化

* Trader 页面：K 线图 + 成交量 + 换手率 + 趋势判断 + 历史相似走势 + 信心度/预期收益率
* UI 风格：毛玻璃 + 低饱和渐变 + 高级交互

---

## 六、Docker 部署

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - AI_MODEL=glm-4.5-flash
      - MAX_MEMORY=4g
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/usr/share/nginx/html
    ports:
      - "3000:3000"
```

* 支持一键启动 → 浏览器访问 → Trader 页面使用 AI 分析

---

## 七、使用说明

1. 启动 Docker：`docker compose up`
2. 打开浏览器访问平台
3. 设置页面配置交易员和策略性格
4. Trader 页面输入股票代码 → 系统自动选择数据源并获取数据
5. AI 分析趋势、输出信心度、预期收益率及交易建议
6. 前端可视化展示 K 线 + 成交量 + 换手率 + 趋势逻辑 + 历史相似走势 + 信心指标

---

## 八、下一步优化方向

* 多股票对比分析
* AI 自适应策略调整交易员性格
* 历史走势回测和收益统计
* 高级指标（量价配合、筹码集中度等）
* 前端图表交互优化（缩放、指标叠加）

---

## 九、总结

* 数据源优化：A股 → efinance，美股 → yfinance，其他市场 → AkShare
* 支持单股分析 + AI 交易员策略性格 + 信心度控制
* 前端可视化升级，支持历史走势参考和信心指标
* Docker 配置优化，一键部署
