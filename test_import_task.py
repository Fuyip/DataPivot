"""
测试导入任务功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 测试用的token（需要先登录获取）
# 这里假设你已经有了token
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_get_card_types():
    """测试获取卡类型"""
    print("\n=== 测试获取卡类型 ===")
    response = requests.get(f"{BASE_URL}/v1/cases/22/case-cards/card-types", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"卡类型数量: {len(data.get('data', []))}")
        print(f"前3个卡类型: {data.get('data', [])[:3]}")
    else:
        print(f"错误: {response.text}")

def test_match_bank():
    """测试银行名称匹配"""
    print("\n=== 测试银行名称匹配 ===")
    test_card_no = "6217001234567890123"
    response = requests.post(
        f"{BASE_URL}/v1/cases/22/case-cards/match-bank",
        headers=headers,
        json={"card_no": test_card_no}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"匹配结果: {data.get('data')}")
    else:
        print(f"错误: {response.text}")

def test_get_import_tasks():
    """测试获取导入任务列表"""
    print("\n=== 测试获取导入任务列表 ===")
    response = requests.get(
        f"{BASE_URL}/v1/cases/22/case-cards/import-tasks",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"任务总数: {data.get('data', {}).get('total', 0)}")
        tasks = data.get('data', {}).get('items', [])
        if tasks:
            print(f"第一个任务: ID={tasks[0].get('id')}, 成功={tasks[0].get('success_count')}, 失败={tasks[0].get('error_count')}")
    else:
        print(f"错误: {response.text}")

def test_rematch_banks():
    """测试重新匹配银行"""
    print("\n=== 测试重新匹配银行 ===")
    response = requests.post(
        f"{BASE_URL}/v1/cases/22/case-cards/rematch-banks",
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"匹配结果: {data.get('data')}")
        print(f"消息: {data.get('message')}")
    else:
        print(f"错误: {response.text}")

if __name__ == "__main__":
    print("开始测试导入任务功能...")
    print("注意: 需要先设置有效的TOKEN")

    # 运行测试
    # test_get_card_types()
    # test_match_bank()
    # test_get_import_tasks()
    # test_rematch_banks()

    print("\n测试完成！")
    print("\n使用说明:")
    print("1. 先登录系统获取token")
    print("2. 将token设置到脚本中的TOKEN变量")
    print("3. 取消注释要测试的函数")
    print("4. 运行脚本: python test_import_task.py")
