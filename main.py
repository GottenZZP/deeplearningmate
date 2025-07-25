#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepLearningMate - 深度学习环境一键安装工具
作者: GottenZZP
版本: 1.0.0
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from cli import cli

if __name__ == '__main__':
    # 检查是否以root权限运行
    if os.geteuid() != 0:
        print("⚠️ 此工具需要管理员权限来安装CUDA")
        print("请使用: sudo python3 main.py [命令]")
        sys.exit(1)
    
    cli()