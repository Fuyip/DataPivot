#!/usr/bin/env python3
"""
修复案件模板SQL文件:
1. 将所有AUTO_INCREMENT值改为从1开始
2. 将所有表中的case_no字段默认值改为{{CASE_CODE}}占位符（案件编号）
3. 删除所有已添加的case_name字段
"""
import re
import sys
import os


def fix_template_sql(input_file, output_file, case_code_placeholder='{{CASE_CODE}}'):
    """
    修复模板SQL文件

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        case_code_placeholder: 案件编号占位符
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 将所有 AUTO_INCREMENT=数字 改为 AUTO_INCREMENT=1
    content = re.sub(
        r'AUTO_INCREMENT=\d+',
        'AUTO_INCREMENT=1',
        content
    )

    # 2. 删除所有case_name字段行
    # 匹配类似: `case_name` varchar(255) DEFAULT '{{CASE_NAME}}' COMMENT '案件名称'
    content = re.sub(
        r',?\s*`case_name`[^\n]*\n',
        '\n',
        content
    )

    # 3. 修改case_no字段的默认值为{{CASE_CODE}}
    # 情况1: 匹配有具体默认值的: `case_no` varchar(255) DEFAULT '3003xpj' COMMENT '案件编号'
    content = re.sub(
        r"(`case_no`[^']*DEFAULT\s+)'[^']*'(\s+COMMENT\s+'案件编号')",
        rf"\1'{case_code_placeholder}'\2",
        content
    )

    # 情况2: 匹配DEFAULT NULL的: `case_no` varchar(255) DEFAULT NULL COMMENT '案件编号'
    content = re.sub(
        r"(`case_no`[^,]*?)DEFAULT\s+NULL(\s+COMMENT\s+'案件编号')",
        rf"\1DEFAULT '{case_code_placeholder}'\2",
        content
    )

    # 4. 清理可能产生的多余逗号（字段定义后紧跟) ENGINE=的情况）
    # 匹配: ,) ENGINE= 或 ,\n) ENGINE=
    content = re.sub(
        r',(\s*)\)',
        r'\1)',
        content
    )

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ 模板文件已修复")
    print(f"  - AUTO_INCREMENT 已重置为 1")
    print(f"  - 已删除所有 case_name 字段")
    print(f"  - case_no 字段默认值已改为: {case_code_placeholder}")
    print(f"  - 输出文件: {output_file}")


if __name__ == '__main__':
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    input_file = os.path.join(project_root, 'sql', 'schema', 'case_template.sql')
    output_file = os.path.join(project_root, 'sql', 'schema', 'case_template_fixed.sql')

    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件 {input_file}")
        sys.exit(1)

    fix_template_sql(input_file, output_file)

    # 自动替换原文件
    os.replace(output_file, input_file)
    print(f"✓ 已替换原文件: {input_file}")

