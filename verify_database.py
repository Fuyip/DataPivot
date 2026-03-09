"""
数据库验证脚本
用于验证导入任务跟踪系统的数据库状态
"""
import pymysql
from datetime import datetime
import json
import os
from pathlib import Path

# 尝试从 .env 文件加载配置
def load_env():
    """加载 .env 文件"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# 加载环境变量
load_env()

# 数据库配置（从环境变量读取）
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', '10.8.0.5'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'fuyip_net_gk'),
    'password': os.getenv('MYSQL_PASSWORD', 'Fuyip235813'),
    'charset': 'utf8mb4'
}

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def get_connection(database=None):
    """获取数据库连接"""
    config = DB_CONFIG.copy()
    if database:
        config['database'] = database
    return pymysql.connect(**config)

def check_import_task_table():
    """检查 import_task 表"""
    print_section("检查1: import_task 表结构")

    conn = get_connection('datapivot')
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'import_task'")
        if not cursor.fetchone():
            print("❌ import_task 表不存在!")
            return False

        print("✅ import_task 表存在")

        # 查看表结构
        cursor.execute("DESC import_task")
        columns = cursor.fetchall()

        print("\n📋 表结构:")
        for col in columns:
            print(f"   {col[0]:20} {col[1]:20} {col[2]:10} {col[3]:10}")

        # 检查索引
        cursor.execute("SHOW INDEX FROM import_task")
        indexes = cursor.fetchall()

        print("\n🔑 索引:")
        for idx in indexes:
            print(f"   {idx[2]:30} 列: {idx[4]}")

        # 统计记录数
        cursor.execute("SELECT COUNT(*) FROM import_task")
        count = cursor.fetchone()[0]
        print(f"\n📊 记录总数: {count}")

        return True

    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def check_case_card_table():
    """检查 case_card 表的 import_task_id 字段"""
    print_section("检查2: case_card 表的 import_task_id 字段")

    # 检查 test01_GXMLM 数据库
    database = 'test01_GXMLM'

    conn = get_connection(database)
    cursor = conn.cursor()

    try:
        # 检查字段是否存在
        cursor.execute(f"SHOW COLUMNS FROM {database}.case_card LIKE 'import_task_id'")
        column = cursor.fetchone()

        if not column:
            print(f"❌ {database}.case_card 表缺少 import_task_id 字段!")
            print("\n💡 执行以下 SQL 添加字段:")
            print(f"   ALTER TABLE {database}.case_card")
            print(f"   ADD COLUMN import_task_id INT DEFAULT NULL COMMENT '导入任务ID' AFTER is_main;")
            print(f"   ALTER TABLE {database}.case_card")
            print(f"   ADD INDEX idx_import_task_id (import_task_id);")
            return False

        print(f"✅ {database}.case_card 表存在 import_task_id 字段")
        print(f"   字段类型: {column[1]}")
        print(f"   允许NULL: {column[2]}")
        print(f"   默认值: {column[4]}")

        # 检查索引
        cursor.execute(f"SHOW INDEX FROM {database}.case_card WHERE Column_name = 'import_task_id'")
        index = cursor.fetchone()

        if index:
            print(f"   索引: {index[2]}")
        else:
            print("   ⚠️  未创建索引")

        # 统计有 import_task_id 的记录
        cursor.execute(f"SELECT COUNT(*) FROM {database}.case_card WHERE import_task_id IS NOT NULL")
        count_with_task = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {database}.case_card")
        count_total = cursor.fetchone()[0]

        print(f"\n📊 记录统计:")
        print(f"   总记录数: {count_total}")
        print(f"   有任务ID: {count_with_task}")
        print(f"   无任务ID: {count_total - count_with_task}")

        return True

    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def check_latest_import_tasks():
    """检查最近的导入任务"""
    print_section("检查3: 最近的导入任务")

    conn = get_connection('datapivot')
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("""
            SELECT *
            FROM import_task
            ORDER BY created_at DESC
            LIMIT 5
        """)

        tasks = cursor.fetchall()

        if not tasks:
            print("📭 暂无导入任务记录")
            return

        print(f"✅ 找到 {len(tasks)} 条最近的任务记录:\n")

        for i, task in enumerate(tasks, 1):
            print(f"任务 {i}:")
            print(f"   ID: {task['id']}")
            print(f"   案件ID: {task['case_id']}")
            print(f"   任务类型: {task['task_type']}")
            print(f"   文件名: {task['file_name']}")
            print(f"   总数: {task['total_count']}")
            print(f"   成功: {task['success_count']}")
            print(f"   失败: {task['error_count']}")
            print(f"   创建人: {task['created_by']}")
            print(f"   创建时间: {task['created_at']}")

            # 解析错误详情
            if task['error_details']:
                try:
                    errors = json.loads(task['error_details'])
                    print(f"   错误数量: {len(errors)}")
                    if errors:
                        print(f"   首个错误: 第{errors[0].get('row')}行 - {errors[0].get('error')}")
                except:
                    print(f"   错误详情: 解析失败")

            print()

    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        cursor.close()
        conn.close()

def check_cards_by_task(task_id):
    """检查指定任务导入的银行卡"""
    print_section(f"检查4: 任务 {task_id} 导入的银行卡")

    database = 'test01_GXMLM'

    conn = get_connection(database)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(f"""
            SELECT
                id,
                card_no,
                bank_name,
                card_type,
                source,
                batch,
                import_task_id
            FROM {database}.case_card
            WHERE import_task_id = %s
            ORDER BY id
        """, (task_id,))

        cards = cursor.fetchall()

        if not cards:
            print(f"📭 任务 {task_id} 没有导入任何银行卡")
            return

        print(f"✅ 找到 {len(cards)} 条银行卡记录:\n")

        # 统计
        with_bank = sum(1 for card in cards if card['bank_name'])
        without_bank = len(cards) - with_bank

        print(f"📊 统计:")
        print(f"   总数: {len(cards)}")
        print(f"   有银行名称: {with_bank}")
        print(f"   无银行名称: {without_bank}")

        # 按批次统计
        batches = {}
        for card in cards:
            batch = card['batch']
            batches[batch] = batches.get(batch, 0) + 1

        print(f"\n📦 批次分布:")
        for batch in sorted(batches.keys()):
            print(f"   批次 {batch}: {batches[batch]} 条")

        # 显示前10条记录
        print(f"\n📋 前10条记录:")
        for i, card in enumerate(cards[:10], 1):
            bank = card['bank_name'] or '(未匹配)'
            print(f"   {i}. ID:{card['id']} - {card['card_no']} - {bank} - {card['source']}")

        # 显示未匹配银行的记录
        unmatched = [card for card in cards if not card['bank_name']]
        if unmatched:
            print(f"\n⚠️  未匹配银行的记录 ({len(unmatched)}条):")
            for i, card in enumerate(unmatched[:5], 1):
                print(f"   {i}. ID:{card['id']} - {card['card_no']} - {card['source']}")

    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        cursor.close()
        conn.close()

def check_bank_bin_table():
    """检查 bank_bin 表"""
    print_section("检查5: bank_bin 表（银行卡BIN库）")

    conn = get_connection('datapivot')
    cursor = conn.cursor()

    try:
        # 统计记录数
        cursor.execute("SELECT COUNT(*) FROM bank_bin")
        count = cursor.fetchone()[0]

        print(f"✅ bank_bin 表记录数: {count}")

        # 显示几个示例
        cursor.execute("SELECT bin, bin_len, card_len, bank_name FROM bank_bin LIMIT 5")
        samples = cursor.fetchall()

        print(f"\n📋 示例记录:")
        for sample in samples:
            print(f"   BIN: {sample[0]} (长度:{sample[1]}) - 卡长:{sample[2]} - {sample[3]}")

        # 检查常见银行
        common_bins = ['621700', '622848', '622202']
        print(f"\n🔍 检查常见银行BIN:")
        for bin_code in common_bins:
            cursor.execute("SELECT bank_name FROM bank_bin WHERE bin = %s LIMIT 1", (bin_code,))
            result = cursor.fetchone()
            if result:
                print(f"   {bin_code}: {result[0]}")
            else:
                print(f"   {bin_code}: ❌ 未找到")

    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        cursor.close()
        conn.close()

def check_sy_bank_table():
    """检查 sy_bank 表"""
    print_section("检查6: sy_bank 表（银行名称映射）")

    conn = get_connection('datapivot')
    cursor = conn.cursor()

    try:
        # 统计记录数
        cursor.execute("SELECT COUNT(*) FROM sy_bank WHERE sys = 'jz'")
        count = cursor.fetchone()[0]

        print(f"✅ sy_bank 表记录数 (sys='jz'): {count}")

        # 显示几个示例
        cursor.execute("SELECT from_bank, to_bank FROM sy_bank WHERE sys = 'jz' LIMIT 5")
        samples = cursor.fetchall()

        print(f"\n📋 示例映射:")
        for sample in samples:
            print(f"   {sample[0]} → {sample[1]}")

    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        cursor.close()
        conn.close()

def check_sys_dict_table():
    """检查 sys_dict 表（卡类型字典）"""
    print_section("检查7: sys_dict 表（卡类型字典）")

    conn = get_connection('datapivot')
    cursor = conn.cursor()

    try:
        # 查询卡类型
        cursor.execute("SELECT d_value, d_label FROM sys_dict WHERE d_type = 'card_type' ORDER BY d_value")
        card_types = cursor.fetchall()

        if not card_types:
            print("❌ 未找到卡类型字典!")
            return

        print(f"✅ 找到 {len(card_types)} 种卡类型:\n")

        for card_type in card_types:
            print(f"   {card_type[0]:10} - {card_type[1]}")

        # 检查测试数据中使用的卡类型
        test_types = ['c15q', 'c15s', 'c30']
        print(f"\n🔍 检查测试数据使用的卡类型:")
        for test_type in test_types:
            cursor.execute("SELECT d_label FROM sys_dict WHERE d_type = 'card_type' AND d_value = %s", (test_type,))
            result = cursor.fetchone()
            if result:
                print(f"   {test_type}: ✅ {result[0]}")
            else:
                print(f"   {test_type}: ❌ 未找到")

    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        cursor.close()
        conn.close()

def run_all_checks():
    """运行所有检查"""
    print("\n" + "="*70)
    print("  数据库验证脚本")
    print("="*70)
    print(f"\n📌 数据库主机: {DB_CONFIG['host']}")
    print(f"📌 数据库用户: {DB_CONFIG['user']}")

    # 检查1: import_task 表
    if not check_import_task_table():
        print("\n⚠️  import_task 表检查失败，请先执行数据库迁移脚本")
        return

    # 检查2: case_card 表
    if not check_case_card_table():
        print("\n⚠️  case_card 表检查失败，请先添加 import_task_id 字段")
        return

    # 检查3: 最近的导入任务
    check_latest_import_tasks()

    # 检查4: 指定任务的银行卡（如果有任务）
    conn = get_connection('datapivot')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM import_task ORDER BY created_at DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        latest_task_id = result[0]
        check_cards_by_task(latest_task_id)

    # 检查5: bank_bin 表
    check_bank_bin_table()

    # 检查6: sy_bank 表
    check_sy_bank_table()

    # 检查7: sys_dict 表
    check_sys_dict_table()

    print_section("验证完成")
    print("✅ 所有检查已完成!")
    print("\n📝 如果发现问题，请参考输出信息进行修复")

if __name__ == "__main__":
    try:
        run_all_checks()
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:  # Access denied
            print(f"\n❌ 数据库连接被拒绝: {e}")
            print("\n💡 可能的原因和解决方案:")
            print("   1. 数据库用户权限问题")
            print("      - 数据库服务器可能只允许特定 IP 连接")
            print("      - 需要数据库管理员为你的 IP 添加访问权限")
            print(f"      - 你的 IP: 10.8.0.49")
            print(f"      - 数据库服务器: {DB_CONFIG['host']}")
            print()
            print("   2. 解决方法:")
            print("      - 联系数据库管理员执行以下 SQL:")
            print(f"        GRANT ALL PRIVILEGES ON *.* TO '{DB_CONFIG['user']}'@'10.8.0.49' IDENTIFIED BY '{DB_CONFIG['password']}';")
            print("        FLUSH PRIVILEGES;")
            print()
            print("   3. 临时解决方案:")
            print("      - 如果后端服务可以正常连接数据库，说明数据库本身是正常的")
            print("      - 可以跳过此验证脚本，直接通过后端 API 测试功能")
            print("      - 使用 test_complex_import.py 进行 API 测试")
        else:
            print(f"\n❌ 数据库连接错误: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
