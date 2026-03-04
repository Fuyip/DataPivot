"""
案件软删除功能测试脚本
用于验证软删除、恢复、永久删除等功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_admin_token_here"  # 需要替换为实际的管理员token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_soft_delete():
    """测试软删除"""
    print("\n=== 测试软删除 ===")
    case_id = 1  # 替换为实际的案件ID

    # 1. 尝试不带confirm参数删除（应该失败）
    print("1. 测试不带confirm参数...")
    response = requests.delete(f"{BASE_URL}/cases/{case_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    # 2. 带confirm参数删除（应该成功）
    print("\n2. 测试带confirm=true参数...")
    response = requests.delete(f"{BASE_URL}/cases/{case_id}?confirm=true", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_get_deleted_cases():
    """测试获取已删除案件列表"""
    print("\n=== 测试获取已删除案件列表 ===")
    response = requests.get(f"{BASE_URL}/cases/deleted/list", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_restore_case():
    """测试恢复案件"""
    print("\n=== 测试恢复案件 ===")
    case_id = 1  # 替换为实际的案件ID

    response = requests.post(f"{BASE_URL}/cases/{case_id}/restore", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_permanent_delete():
    """测试永久删除"""
    print("\n=== 测试永久删除 ===")
    case_id = 1  # 替换为实际的案件ID

    # 1. 尝试删除未软删除的案件（应该失败）
    print("1. 测试删除未软删除的案件...")
    response = requests.delete(f"{BASE_URL}/cases/{case_id}/permanent?confirm=true", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    # 2. 先软删除，再永久删除
    print("\n2. 先执行软删除...")
    response = requests.delete(f"{BASE_URL}/cases/{case_id}?confirm=true", headers=headers)
    print(f"状态码: {response.status_code}")

    print("\n3. 再执行永久删除...")
    response = requests.delete(f"{BASE_URL}/cases/{case_id}/permanent?confirm=true", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_case_list_filter():
    """测试案件列表是否过滤已删除案件"""
    print("\n=== 测试案件列表过滤 ===")
    response = requests.get(f"{BASE_URL}/cases", headers=headers)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"案件总数: {data['data']['total']}")
    print(f"返回案件: {len(data['data']['items'])} 条")


if __name__ == "__main__":
    print("案件软删除功能测试")
    print("=" * 50)
    print("注意: 请先修改脚本中的 TOKEN 和 case_id")
    print("=" * 50)

    # 运行测试
    try:
        # test_soft_delete()
        # test_get_deleted_cases()
        # test_restore_case()
        # test_permanent_delete()
        # test_case_list_filter()

        print("\n请取消注释要测试的函数")
    except Exception as e:
        print(f"\n测试出错: {str(e)}")
