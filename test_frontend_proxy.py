import requests
import json

def test_frontend_proxy():
    """测试前端代理是否正常工作"""
    try:
        # 通过前端代理访问后端服务
        response = requests.get("http://localhost:3000/api/v1")
        print(f"通过前端代理访问后端状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("无法通过前端代理连接到后端服务，请检查代理配置")
        return False

def test_frontend_ai_test_connection():
    """通过前端代理测试AI连接测试接口"""
    try:
        data = {
            "api_key": "test",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.1
        }
        response = requests.post(
            "http://localhost:3000/api/v1/ai/test-connection",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        print(f"通过前端代理访问AI连接测试接口状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("无法通过前端代理连接到AI连接测试接口，请检查代理配置")
        return False

if __name__ == "__main__":
    print("测试前端代理是否正常工作...")
    test_frontend_proxy()
    print("\n通过前端代理测试AI连接测试接口...")
    test_frontend_ai_test_connection()