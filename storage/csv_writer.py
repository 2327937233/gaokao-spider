# -*- coding: utf-8 -*-
"""
CSV 文件写入模块
将采集的数据保存为 CSV 格式
"""

import os
import csv
from datetime import datetime

from config import CLEANED_DIR, OUTPUT_COLUMNS, CSV_HEADERS
from utils.logger import get_logger

logger = get_logger(__name__)


class CSVWriter:
    """CSV 写入器"""

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or CLEANED_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def _write_header(self, writer):
        """写入中文表头"""
        chinese_header = {col: CSV_HEADERS.get(col, col) for col in OUTPUT_COLUMNS}
        writer.writerow(chinese_header)

    def write(self, data, filename=None):
        """
        将数据写入 CSV 文件

        Args:
            data: 数据字典列表
            filename: 输出文件名，默认使用当前时间命名

        Returns:
            str: 保存的文件路径
        """
        if not data:
            logger.warning("数据为空，未写入 CSV")
            return ""

        if filename is None:
            filename = f"gaokao_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # 确保文件名以 .csv 结尾
        if not filename.endswith(".csv"):
            filename += ".csv"

        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
                # 写入中文表头
                self._write_header(writer)

                for record in data:
                    # 确保所有字段都存在
                    row = {col: record.get(col, "") for col in OUTPUT_COLUMNS}
                    writer.writerow(row)

            logger.info(f"CSV 写入成功: {filepath}，共 {len(data)} 条记录")
            return filepath

        except Exception as e:
            logger.error(f"CSV 写入失败 [{filepath}]: {e}")
            return ""

    def append(self, data, filename):
        """
        追加数据到已有 CSV 文件

        Args:
            data: 数据字典列表
            filename: CSV 文件名

        Returns:
            str: 文件路径
        """
        if not data:
            return ""

        filepath = os.path.join(self.output_dir, filename)
        file_exists = os.path.exists(filepath)

        try:
            with open(filepath, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)

                if not file_exists:
                    self._write_header(writer)

                for record in data:
                    row = {col: record.get(col, "") for col in OUTPUT_COLUMNS}
                    writer.writerow(row)

            logger.info(f"CSV 追加成功: {filepath}，本次追加 {len(data)} 条记录")
            return filepath

        except Exception as e:
            logger.error(f"CSV 追加失败 [{filepath}]: {e}")
            return ""
