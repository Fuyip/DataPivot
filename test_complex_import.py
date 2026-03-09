"""
复杂导入测试脚本
用于测试复杂导入测试数据的各种场景
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"
CASE_ID = 22  # 测试案件ID

# 测试用的token（需要先登录获取）
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_import_complex_data():
    """测试导入复杂测试数据"""
    print_section("测试1: 导入复杂测试数据")

    file_path = "/Users/yipf/Desktop/复杂导入测试数据.xlsx"

    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return None

    print(f"📁 准备导入文件: {file_path}")

    with open(file_path, 'rb') as f:
        files = {'file': ('复杂导入测试数据.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(
            f"{BASE_URL}/v1/cases/{CASE_ID}/case-cards/import",
            headers={"Authorization": f"Bearer {TOKEN}"},
            files=files
        )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        result = data.get('data', {})

        print(f"\n✅ 导入完成!")
        print(f"   总记录数: {result.get('total_count', 0)}")
        print(f"   成功数: {result.get('success_count', 0)}")
        print(f"   失败数: {result.get('error_count', 0)}")
        print(f"   任务ID: {result.get('task_id', 'N/A')}")

        errors = result.get('errors', [])
        if errors:
            print(f"\n⚠️  错误详情 (前10条):")
            for i, error in enumerate(errors[:10], 1):
                print(f"   {i}. 第{error.get('row')}行 - 卡号: {error.get('card_no')} - {error.get('error')}")

        return result.get('task_id')
    else:
        print(f"❌ 导入失败: {response.text}")
        return None

def test_get_import_tasks():
    """测试获取导入任务列表"""
    print_section("测试2: 获取导入任务列表")

    response = requests.get(
        f"{BASE_URL}/v1/cases/{CASE_ID}/case-cards/import-tasks",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        result = data.get('data', {})

        print(f"\n✅ 获取成功!")
        print(f"   任务总数: {result.get('total', 0)}")

        tasks = result.get('items', [])
        if tasks:
            print(f"\n📋 最近的任务:")
            for i, task in enumerate(tasks[:5], 1):
                print(f"\n   任务 {i}:")
                print(f"      ID: {task.get('id')}")
                print(f"      文件名: {task.get('file_name')}")
                print(f"      总数: {task.get('total_count')}")
                print(f"      成功: {task.get('success_count')}")
                print(f"      失败: {task.get('error_count')}")
                print(f"      创建时间: {task.get('created_at')}")

        return tasks[0] if tasks else None
    else:
        print(f"❌ 获取失败: {response.text}")
        return None

def test_view_task_errors(task_id):
    """测试查看任务错误详情"""
    print_section(f"测试3: 查看任务 {task_id} 的错误详情")

    response = requests.get(
        f"{BASE_URL}/v1/cases/{CASE_ID}/case-cards/import-tasks",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )

    if response.status_code == 200:
        data = response.json()
        tasks = data.get('data', {}).get('items', [])

        task = next((t for t in tasks if t['id'] == task_id), None)

        if task:
            error_details = task.get('error_details')
            if error_details:
                try:
                    errors = json.loads(error_details)
                    print(f"\n✅ 找到 {len(errors)} 条错误记录:")
                    for i, error in enumerate(errors, 1):
                        print(f"\n   错误 {i}:")
                        print(f"      行号: {error.get('row')}")
                        print(f"      卡号: {error.get('card_no')}")
                        print(f"      错误: {error.get('error')}")
                except json.JSONDecodeError:
                    print(f"⚠️  错误详情格式不正确")
            else:
                print(f"✅ 该任务没有错误记录")
        else:
            print(f"❌ 未找到任务 ID: {task_id}")
    else:
        print(f"❌ 获取失败: {response.text}")

def test_check_unmatched_banks():
    """测试检查未匹配银行的记录"""
    print_section("测试4: 检查未匹配银行的记录")

    response = requests.get(
        f"{BASE_URL}/v1/cases/{CASE_ID}/case-cards",
        headers=headers,
        params={"page": 1, "page_size": 100}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        cards = data.get('data', {}).get('items', [])

        unmatched = [card for card in cards if not card.get('bank_name')]

        print(f"\n✅ 查询成功!")
        print(f"   总记录数: {len(cards)}")
        print(f"   未匹配银行: {len(unmatched)}")

        if unmatched:
            print(f"\n⚠️  未匹配银行的记录:")
            for i, card in enumerate(unmatched[:10], 1):
                print(f"   {i}. ID: {card.get('id')} - 卡号: {card.get('card_no')} - 卡主: {card.get('source')}")

        return len(unmatched)
    else:
        print(f"❌ 查询失败: {response.text}")
        return 0

def test_rematch_banks():
    """测试重新匹配银行"""
    print_section("测试5: 一键重新匹配银行")

    response = requests.post(
        f"{BASE_URL}/v1/cases/{CASE_ID}/case-cards/rematch-banks",
        headers=headers
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        result = data.get('data', {})

        print(f"\n✅ 匹配完成!")
        print(f"   总共未匹配: {result.get('total_unmatched', 0)}")
        print(f"   成功匹配: {result.get('matched_count', 0)}")
        print(f"   仍未匹配: {result.get('still_unmatched', 0)}")
        print(f"\n💡 {data.get('message', '')}")
    else:
        print(f"❌ 匹配失败: {response.text}")

def test_delete_task_cards(task_id):
    """测试删除任务相关的所有银行卡"""
    print_section(f"测试6: 删除任务 {task_id} 的所有银行卡")

    # 先确认是否要删除
    print(f"⚠️  警告: 此操作将删除任务 {task_id} 导入的所有银行卡!")
    confirm = input("是否继续? (yes/no): ")

    if confirm.lower() != 'yes':
        print("❌ 已取消删除操作")
        return

    response = requests.delete(
        f"{BASE_URL}/v1/cases/{CASE_ID}/case-cards/import-tasks/{task_id}",
        headers=headers
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        result = data.get('data', {})

        print(f"\n✅ 删除完成!")
        print(f"   预期删除: {result.get('expected_count', 0)}")
        print(f"   实际删除: {result.get('deleted_count', 0)}")
        print(f"\n💡 {data.get('message', '')}")
    else:
        print(f"❌ 删除失败: {response.text}")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  复杂导入测试脚本")
    print("="*60)
    print(f"\n📌 测试案件ID: {CASE_ID}")
    print(f"📌 API地址: {BASE_URL}")
    print(f"📌 Token: {'已设置' if TOKEN != 'your_token_here' else '未设置 ⚠️'}")

    if TOKEN == "your_token_here":
        print("\n❌ 错误: 请先设置有效的 TOKEN")
        print("\n使用说明:")
        print("1. 登录系统获取 token")
        print("2. 将 token 设置到脚本中的 TOKEN 变量")
        print("3. 运行脚本: python test_complex_import.py")
        return

    # 测试1: 导入复杂数据
    task_id = test_import_complex_data()

    if not task_id:
        print("\n❌ 导入失败，无法继续后续测试")
        return

    # 测试2: 获取导入任务列表
    latest_task = test_get_import_tasks()

    # 测试3: 查看任务错误详情
    if task_id:
        test_view_task_errors(task_id)

    # 测试4: 检查未匹配银行的记录
    unmatched_count = test_check_unmatched_banks()

    # 测试5: 重新匹配银行
    if unmatched_count > 0:
        test_rematch_banks()

        # 再次检查未匹配记录
        test_check_unmatched_banks()

    # 测试6: 删除任务数据（可选）
    # test_delete_task_cards(task_id)

    print_section("测试完成")
    print("✅ 所有测试已完成!")
    print("\n📝 注意事项:")
    print("   - 如需删除测试数据，请取消注释 test_delete_task_cards() 调用")
    print("   - 删除操作不可逆，请谨慎操作")
    print("   - 建议在测试环境中运行此脚本")

if __name__ == "__main__":
    # 可以单独运行某个测试
    # test_import_complex_data()
    # test_get_import_tasks()
    # test_check_unmatched_banks()
    # test_rematch_banks()

    # 或运行所有测试
    run_all_tests()
