import requests
import json

# 读取用户的AI配置
def get_user_ai_config():
    # 这里可以替换为您当前的AI配置
    return {
        "openaiApiKey": "",  # 请替换为您的API密钥
        "apiBaseUrl": "https://openai.com/v1",  # 请替换为您的API地址
        "aiModelName": "gpt-3.5-turbo",  # 请替换为您的模型名称
        "temperature": 0.1
    }

# 测试AI连接
def test_ai_connection():
    url = "http://localhost:8000/api/v1/ai/test-connection"
    ai_settings = get_user_ai_config()
    
    print("正在使用以下配置测试AI连接：")
    print(json.dumps(ai_settings, indent=2, ensure_ascii=False))
    print("\n发送请求...")
    
    try:
        response = requests.post(url, json=ai_settings, timeout=30)
        print(f"\n状态码: {response.status_code}")
        
        # 解析响应
        try:
            response_json = response.json()
            print(f"响应内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            
            # 分析错误原因
            if not response_json.get("success"):
                error_message = response_json.get("message", "")
                print(f"\n错误分析：")
                
                if "401" in error_message:
                    print("- 401认证错误：请检查API密钥是否正确")
                elif "404" in error_message:
                    print("- 404错误：请检查API基础URL或模型名称是否正确")
                elif "connect" in error_message.lower():
                    print("- 连接错误：请检查网络连接或API基础URL是否正确")
                elif "invalid" in error_message.lower():
                    print("- 无效请求：请检查请求参数是否正确")
                else:
                    print(f"- 其他错误：{error_message}")
                    
        except json.JSONDecodeError:
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n连接错误：无法连接到后端服务器")
        print("请检查：")
        print("1. 后端服务器是否正在运行")
        print("2. 网络连接是否正常")
    except requests.exceptions.Timeout:
        print("\n超时错误：请求超时")
        print("请检查：")
        print("1. 网络连接是否稳定")
        print("2. API基础URL是否正确")
    except Exception as e:
        print(f"\n请求失败: {str(e)}")

if __name__ == "__main__":
    test_ai_connection()