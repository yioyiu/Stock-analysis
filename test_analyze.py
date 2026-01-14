import requests
import json
from datetime import datetime, timedelta

# 获取最近30天的日期范围
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# 测试请求数据
data = {
    "symbol": "sh000001",  # 尝试使用带交易所前缀的股票代码
    "start_date": start_date,
    "end_date": end_date,
    "strategy": {
        "risk_preference": "medium",
        "trend_sensitivity": "medium",
        "bias": "neutral"
    }
}

# 发送请求
try:
    response = requests.post(
        "http://localhost:8000/api/v1/ai/analyze",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 422:
        print(f"详细错误信息: {json.dumps(response.json(), indent=2)}")
    elif response.status_code == 500:
        print(f"服务器错误: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")