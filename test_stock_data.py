import requests
import json

# 测试获取股票历史数据
def test_stock_history():
    url = "http://localhost:8000/api/v1/stock/history"
    
    # 测试A股股票
    test_symbols = ["sh000001", "sz000001", "AAPL"]
    
    for symbol in test_symbols:
        print(f"\n测试股票: {symbol}")
        try:
            response = requests.get(url, params={"symbol": symbol})
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"数据类型: {'真实数据' if result.get('data') and len(result['data']) > 0 else '模拟数据'}")
                if result.get('data'):
                    print(f"数据条数: {len(result['data'])}")
                    print(f"第一条数据: {json.dumps(result['data'][0], indent=2, ensure_ascii=False)}")
                    print(f"最后一条数据: {json.dumps(result['data'][-1], indent=2, ensure_ascii=False)}")
            else:
                print(f"错误信息: {response.text}")
        except Exception as e:
            print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    test_stock_history()
