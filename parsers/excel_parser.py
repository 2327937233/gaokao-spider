# -*- coding: utf-8 -*-
"""
Excel 文件解析模块
支持 .xls 和 .xlsx 格式
"""

import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)


class ExcelParser:
    """Excel 解析器"""

    @staticmethod
    def parse(filepath, sheet_name=None, header=0):
        """
        解析 Excel 文件

        Args:
            filepath: Excel 文件路径
            sheet_name: 指定工作表名称或索引，None 表示读取所有工作表
            header: 表头行号，默认第0行

        Returns:
            list: DataFrame 列表（如果读取所有工作表，每个工作表一个 DataFrame）
        """
        if not filepath:
            logger.warning("Excel 文件路径为空")
            return []

        tables = []

        try:
            if sheet_name is not None:
                # 读取指定工作表
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=header)
                if not df.empty:
                    tables.append(df)
            else:
                # 读取所有工作表
                xls = pd.ExcelFile(filepath)
                for name in xls.sheet_names:
                    try:
                        df = pd.read_excel(filepath, sheet_name=name, header=header)
                        if not df.empty:
                            tables.append(df)
                            logger.info(f"读取工作表: {name}, 行数: {len(df)}")
                    except Exception as e:
                        logger.warning(f"读取工作表 [{name}] 失败: {e}")

            logger.info(f"Excel 解析完成，共 {len(tables)} 个表格")
            return tables

        except Exception as e:
            logger.error(f"Excel 解析失败 [{filepath}]: {e}")
            return []

    @staticmethod
    def parse_all_sheets(filepath, header=0):
        """
        读取 Excel 文件中的所有工作表

        Args:
            filepath: Excel 文件路径
            header: 表头行号

        Returns:
            dict: {sheet_name: DataFrame} 字典
        """
        if not filepath:
            return {}

        result = {}
        try:
            xls = pd.ExcelFile(filepath)
            for name in xls.sheet_names:
                try:
                    df = pd.read_excel(filepath, sheet_name=name, header=header)
                    if not df.empty:
                        result[name] = df
                except Exception as e:
                    logger.warning(f"读取工作表 [{name}] 失败: {e}")
            return result
        except Exception as e:
            logger.error(f"Excel 全表解析失败 [{filepath}]: {e}")
            return {}
