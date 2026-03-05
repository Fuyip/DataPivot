"""
测试模板创建功能
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 1. 先登录获取token
login_data = {
    "username": "admin",
    "password": "admin123"
}

print("1. 登录获取token...")
response = requests.post(f"{BASE_URL}/v1/auth/login", json=login_data)
print(f"登录响应状态码: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    token = result.get("data", {}).get("access_token")
    print(f"Token获取成功: {token[:50]}...")
else:
    print(f"登录失败: {response.text}")
    exit(1)

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 查询当前模板列表
print("\n2. 查询当前模板列表...")
response = requests.get(f"{BASE_URL}/v1/import-rules/templates", headers=headers)
print(f"查询响应状态码: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    templates = result.get("data", {}).get("items", [])
    print(f"当前模板数量: {len(templates)}")
    for t in templates:
        print(f"  - ID: {t['id']}, 名称: {t['template_name']}, 默认: {t['is_default']}")
else:
    print(f"查询失败: {response.text}")

# 3. 创建新模板
print("\n3. 创建新测试模板...")
new_template = {
    "template_name": "测试模板_" + str(int(requests.get("http://worldtimeapi.org/api/timezone/Asia/Shanghai").json()["unixtime"])),
    "description": "这是一个测试模板，用于验证创建功能",
    "is_active": True
}
print(f"创建数据: {json.dumps(new_template, ensure_ascii=False)}")

response = requests.post(f"{BASE_URL}/v1/import-rules/templates", headers=headers, json=new_template)
print(f"创建响应状态码: {response.status_code}")
print(f"创建响应内容: {response.text}")

if response.status_code == 200:
    result = response.json()
    if result.get("code") == 200:
        created_template = result.get("data", {})
        print(f"✅ 模板创建成功!")
        print(f"  - ID: {created_template.get('id')}")
        print(f"  - 名称: {created_template.get('template_name')}")
        print(f"  - 描述: {created_template.get('description')}")

        # 4. 再次查询模板列表，验证新模板是否存在
        print("\n4. 再次查询模板列表，验证新模板...")
        response = requests.get(f"{BASE_URL}/v1/import-rules/templates", headers=headers)
        if response.status_code == 200:
            result = response.json()
            templates = result.get("data", {}).get("items", [])
            print(f"当前模板数量: {len(templates)}")
            for t in templates:
                print(f"  - ID: {t['id']}, 名称: {t['template_name']}")
    else:
        print(f"❌ 创建失败: {result.get('message')}")
else:
    print(f"❌ 创建失败: {response.text}")
