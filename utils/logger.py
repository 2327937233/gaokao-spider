# -*- coding: utf-8 -*-
"""
日志工具模块
提供统一的日志记录功能
"""

import logging
import os
import sys
from datetime import datetime


def get_logger(name="gaokao_spider"):
    """
    获取配置好的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"spider_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
