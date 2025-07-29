"""
測試模組
包含所有單元測試和集成測試
"""

# 測試配置
import os
import sys

# 確保能夠導入 app 模組
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

__all__ = [] 