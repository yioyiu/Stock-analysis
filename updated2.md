# Trader 页面 + AI 交易员系统重构 —— 技术设计与实施方案

> 目标：将原有智能筛股平台升级为**单股分析 + AI 交易员 + 可视化 + 历史趋势参考**的工程级系统。用户通过浏览器输入股票代码即可获取分析结果，并可配置交易员策略性格。

---

## 一、更新概述

1. **Trader 页面**

   * 输入股票代码，AI 获取历史 K 线数据
   * 根据策略判断多头或空头趋势
   * 显示详细逻辑分析
   * 历史类似走势参考及涨跌结果

2. **设置页面**

   * 配置交易员（AI API 接口）
   * 配置交易员性格（策略参数）

3. **可视化升级**

   * K 线图、成交量、换手率图
   * 低饱和渐变 + 毛玻璃效果

4. **AI 分析逻辑**

   * 支持策略化趋势判断
   * 输出结构化 JSON，包括趋势、逻辑说明、历史相似走势

---

## 二、数据获取与处理

* 使用 **AkShare** 获取股票历史 K 线数据
* 支持最近 N 根交易日
* 输出结构化 DataFrame 供 AI 分析和可视化

```python
import akshare as ak

def get_stock_history(stock_code, start_date, end_date, period='daily'):
    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )
    return df
```

---

## 三、Trader 页面功能

1. 输入股票代码 → 获取历史数据
2. K 线可视化（ECharts / TradingView / Plotly）
3. AI 趋势判断

   * 输入：历史 K 线数据 + 交易员策略
   * 输出：趋势、多头/空头判断、逻辑说明、历史相似走势

### AI 输入示例

```json
{
  "stock": "000001",
  "history_kline": [...],
  "volume": [...],
  "turnover_rate": [...],
  "strategy": {"risk_preference": "medium", "trend_sensitivity": "high"}
}
```

### AI 输出示例

```json
{
  "trend": "多头",
  "logic": "过去20日收盘价形成上涨通道，成交量逐步放大，换手率保持低位平稳",
  "historical_similar_patterns": [
    {"pattern_date": "2023-01-01", "result": "上涨"},
    {"pattern_date": "2022-08-01", "result": "上涨"}
  ]
}
```

---

## 四、设置页面功能

* 配置交易员 API（模型类型、URL、API Key）
* 配置交易员性格（风险偏好、趋势敏感度、多空偏好）

```json
{
  "trader_name": "AlphaTrader",
  "ai_model": "glm-4.5-flash",
  "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
  "strategy": {"risk_preference": "medium", "trend_sensitivity": "high", "bias": "long"}
}
```

---

## 五、前端可视化更新

* Trader 页面：K 线图 + 成交量 + 换手率 + 趋势判断 + 历史相似走势
* UI 风格：毛玻璃 + 低饱和渐变 + 高级交互

### 可视化组件结构

```
┌──────────────┐
│ K线主图     │
├──────────────┤
│ 成交量柱状图 │
├──────────────┤
│ 换手率折线图 │
└──────────────┘
```

---

## 六、Docker 部署更新

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
4. Trader 页面输入股票代码
5. 系统自动获取数据并分析趋势
6. 可视化显示 K 线 + 成交量 + 换手率 + 趋势逻辑 + 历史相似走势

---

## 八、下一步优化方向

* 支持多股票对比分析
* AI 自适应策略，自动调整交易员性格
* 历史走势回测和收益统计
* 增加高级指标（量价配合、筹码集中度等）
* 前端图表交互优化（缩放、指标叠加）

---

## 九、总结

* 重构为 Trader 单股分析系统 + AI 交易员
* 支持策略化多空趋势判断 + 详细逻辑说明
* 设置页面可配置交易员和策略参数
* 前端可视化升级，支持历史走势参考
* Docker 配置优化，一键部署
