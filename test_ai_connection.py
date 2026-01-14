import requests
import json

# 测试AI连接
def test_ai_connection():
    url = "http://localhost:8000/api/v1/ai/test-connection"
    
    # 配置AI模型设置
    ai_settings = {
        "openaiApiKey": "",  # 请替换为您的API密钥
        "apiBaseUrl": "https://api.openai.com/v1",  # 或您的自定义API地址
        "aiModelName": "gpt-3.5-turbo",  # 或您的自定义模型名称
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, json=ai_settings)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    test_ai_connection()