# 项目更新：AI 筛股能力与系统升级

## 更新概述

本次项目更新旨在提升 AI 筛股平台的智能分析能力，使其能够：

1. 基于股票历史 **K 线、成交量、换手率等基本面信息**，分析资金筹码行为  
2. 支持用户自定义筛选条件，AI 自动判断符合条件的股票  
3. 输出结构化分析结果，并在前端可视化显示  
4. 更新 Docker 部署配置，确保 AI 模块与前端/后端协同运行  

更新后的系统不再局限于单一策略，而是形成**通用分析思考框架**，为未来多种筛股策略打下基础。

---

## 技术架构更新

### 1. 数据来源

- 使用 **AkShare** 获取股票历史数据：
  - K 线（开盘、收盘、最高、最低）
  - 成交量
  - 换手率
- 支持获取最近 N 根交易日数据（可配置）
- 数据用于 AI 分析及前端可视化

#### 示例 Python 调用
```python
import akshare as ak

df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20230901",
    end_date="20240101",
    adjust="qfq"
)
last_n = df.tail(100)  # 获取最近 100 根交易日数据

2. 特征计算（Python 预处理）

在将数据传给 AI 前，先将原始数据结构化为可分析特征：
| 特征                                 | 含义        |
| ---------------------------------- | --------- |
| avg_volume_short / avg_volume_long | 短期与中期量能比较 |
| turnover_mean                      | 平均换手率     |
| price_range                        | 价格振幅、波动性  |
| kline_shadow_ratio                 | 上影线/下影线比例 |
| consolidation_days                 | 横盘整理天数    |
| volatility_trend                   | 波动趋势      |



3. AI 分析逻辑（通用思考能力）

模型：glm-4.5-flash 或同类大模型

输入：结构化特征 + 用户自定义筛选条件

AI 能够：

根据价格、成交量、换手率及 K 线形态分析资金筹码变化

推理潜在主力或散户行为模式

根据条件输出符合筛选要求的股票，并给出分析理由

输出示例（结构化 JSON）：
{
  "stock": "000001",
  "meets_conditions": true,
  "analysis_reason": "价格横盘整理，成交量逐步放大，换手率缓慢抬升，显示潜在资金集中",
  "risk_warning": "短期若突破区间需谨慎"
}

4. 前端展示更新

新增 AI 筛股分析面板

显示内容：

股票列表及筛选结果

可视化 K 线图、成交量图、换手率图

AI 输出分析理由及风险提示

UI 风格：

低饱和渐变色

透明毛玻璃效果

高级交互设计，提升投研体验

5. Docker 部署更新

AI Agent 独立服务：backend/ai_agents/strategy_agent.py

Docker Compose 更新示例：
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


