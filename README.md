# 智能股票筛选应用

一个基于React+FastAPI+AI的智能股票筛选和分析应用，支持多市场股票数据获取、AI趋势分析、K线图可视化等功能。

## 功能特性

### 数据获取与缓存
- 支持A股、港股、美股等多市场股票数据获取
- 自动选择合适的数据来源（AkShare、efinance、yfinance）
- 本地缓存股票历史数据，避免重复请求
- 数据有效期管理，自动提示数据更新

### AI分析
- 基于LangChain+OpenAI的股票趋势分析
- 支持自定义分析策略（风险偏好、趋势敏感度、多空偏好）
- 提供详细的分析逻辑和置信度
- 识别支撑区间和压力区间

### 可视化图表
- K线图展示，支持红涨绿跌显示
- 成交量和换手率图表
- 支撑和压力区间可视化
- 可交互图例，支持切换图表显示
- 响应式设计，适应不同屏幕尺寸

### 用户体验
- 分步进度弹窗，清晰展示操作流程
- 详细的错误提示和操作指导
- 支持多种市场和股票代码格式
- 直观的分析结果展示

## 技术栈

### 前端
- React 18+：构建用户界面
- ECharts：数据可视化
- Axios：HTTP请求
- CSS3：样式设计

### 后端
- FastAPI：API服务框架
- Pydantic：数据验证
- LangChain：AI应用开发框架
- OpenAI API：大语言模型
- Pandas：数据处理
- AkShare/efinance/yfinance：股票数据获取

## 安装与运行

### 环境要求
- Python 3.9+
- Node.js 16+
- npm 8+

### 后端安装与运行

1. 进入后端目录
```bash
cd backend
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行后端服务
```bash
python main.py
```

后端服务将运行在 `http://0.0.0.0:8000`

### 前端安装与运行

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 运行前端开发服务器
```bash
npm run dev
```

前端服务将运行在 `http://localhost:3000`

## 配置说明

### AI配置

1. 打开应用，点击右上角设置图标
2. 填写AI模型参数：
   - API密钥：从OpenAI或其他LLM提供商获取
   - API基础地址：根据使用的模型提供商填写
   - AI模型名称：如gpt-3.5-turbo、gpt-4等
   - 温度值：控制输出的随机性（0-1）
3. 保存配置

### 数据来源配置

应用会根据股票代码自动选择合适的数据来源：
- A股：使用efinance或AkShare
- 港股：使用AkShare
- 美股：使用yfinance

## 使用说明

### 1. 选择市场和股票代码

- 在"分析设置"中选择股票市场（A股、港股、美股）
- 输入股票代码
- 例如：A股输入`000001`，港股输入`00700`，美股输入`AAPL`

### 2. 获取历史数据

- 点击"开始获取"按钮
- 等待进度弹窗显示完成
- 系统将获取并缓存该股票的全部历史数据

### 3. 配置分析策略

- 设置风险偏好：低风险、中风险、高风险
- 设置趋势敏感度：低敏感度、中敏感度、高敏感度
- 设置多空偏好：中性、多头偏好、空头偏好

### 4. AI分析

- 点击"开始分析"按钮
- 等待进度弹窗显示完成
- 查看AI分析结果，包括趋势判断、支撑/压力区间等

### 5. 查看可视化图表

- 分析完成后，自动显示K线图、成交量图和换手率图
- 支持点击图例切换图表显示
- 悬停查看详细数据

## 项目结构

```
smart-stock-screening/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/             # API端点
│   │   │   └── endpoints/   # 具体API路由
│   │   ├── core/            # 核心配置
│   │   ├── schemas/         # 数据模型
│   │   └── services/        # 业务逻辑
│   │       ├── ai_analysis_service.py  # AI分析服务
│   │       └── stock_data_service.py   # 股票数据服务
│   ├── main.py              # 后端入口
│   └── requirements.txt     # 后端依赖
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── components/      # React组件
│   │   │   ├── Trader.jsx       # 主交易组件
│   │   │   ├── StockChart.jsx   # 股票图表组件
│   │   │   └── ProgressModal.jsx # 进度弹窗组件
│   │   ├── services/        # API服务
│   │   │   └── api.js       # API请求封装
│   │   └── App.jsx          # 应用入口
│   ├── index.html           # HTML模板
│   └── package.json         # 前端依赖
└── README.md                # 项目说明文档
```

## 常见问题

### 1. 为什么获取数据失败？

- 检查股票代码是否正确
- 确认选择了正确的市场
- 检查网络连接
- 查看浏览器控制台或后端日志获取详细错误信息

### 2. 为什么AI分析失败？

- 检查AI配置是否完整
- 确认API密钥有效
- 检查网络连接
- 查看浏览器控制台或后端日志获取详细错误信息

### 3. 为什么图表显示异常？

- 确认已成功获取股票数据
- 检查浏览器兼容性
- 查看浏览器控制台获取详细错误信息

## 开发与扩展

### 后端扩展

1. 新增数据来源：在`stock_data_service.py`中添加新的数据获取逻辑
2. 新增AI模型：在`ai_analysis_service.py`中集成新的LLM模型
3. 新增API端点：在`api/endpoints/`目录下添加新的路由处理函数

### 前端扩展

1. 新增图表类型：在`StockChart.jsx`中添加新的ECharts配置
2. 新增分析指标：在AI分析服务中添加新的分析维度
3. 优化UI设计：修改CSS样式或组件布局


