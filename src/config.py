#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置文件
统一管理路径配置和其他项目设置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = DATA_DIR / "outputs"
LOGS_DIR = DATA_DIR / "logs"

# 源代码目录
SRC_DIR = PROJECT_ROOT / "src"

# 测试目录
TESTS_DIR = PROJECT_ROOT / "tests"

# 文档目录
DOCS_DIR = PROJECT_ROOT / "docs"

# 确保目录存在
def ensure_dirs():
    """确保所有必要的目录都存在"""
    for dir_path in [DATA_DIR, OUTPUTS_DIR, LOGS_DIR, TESTS_DIR, DOCS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

# 获取输出文件路径
def get_output_path(filename: str) -> Path:
    """获取输出文件的完整路径"""
    ensure_dirs()
    return OUTPUTS_DIR / filename

# 获取日志文件路径
def get_log_path(filename: str) -> Path:
    """获取日志文件的完整路径"""
    ensure_dirs()
    return LOGS_DIR / filename

# 项目信息
PROJECT_NAME = "PumaCrawler"
PROJECT_VERSION = "2.0.0"
PROJECT_DESCRIPTION = "PUMA商品信息爬虫工具"

# 爬虫配置
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

# 输出格式配置
DEFAULT_OUTPUT_FORMAT = "json"
DEFAULT_ENCODING = "utf-8"

if __name__ == "__main__":
    # 测试配置
    ensure_dirs()
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"数据目录: {DATA_DIR}")
    print(f"输出目录: {OUTPUTS_DIR}")
    print(f"日志目录: {LOGS_DIR}")
    print(f"源码目录: {SRC_DIR}")