"""
核心配置模块
复用根目录的配置，并提供统一的配置访问接口
"""
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from config import config, Settings

# 导出配置实例供其他模块使用
__all__ = ["config", "Settings"]
