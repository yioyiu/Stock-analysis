import requests
import json

def test_backend_connection():
    """测试后端服务连接"""
    try:
        # 测试后端服务是否运行
        response = requests.get("http://localhost:8000")
        print(f"后端服务状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("无法连接到后端服务，请检查服务是否正在运行")
        return False

def test_ai_test_connection():
    """测试AI连接测试接口"""
    try:
        data = {
            "api_key": "test",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.1
        }
        response = requests.post(
            "http://localhost:8000/api/v1/ai/test-connection",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        print(f"AI连接测试接口状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("无法连接到AI连接测试接口，请检查后端服务是否正在运行")
        return False

if __name__ == "__main__":
    print("测试后端服务连接...")
    test_backend_connection()
    print("\n测试AI连接测试接口...")
    test_ai_test_connection()