# -*- coding: utf-8 -*-
"""
PDF 文件解析模块
使用 pdfplumber 提取文字型表格
对于扫描型PDF给出保底处理方案
"""

import os
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFParser:
    """PDF 解析器"""

    @staticmethod
    def parse(filepath):
        """
        解析 PDF 文件中的表格

        Args:
            filepath: PDF 文件路径

        Returns:
            list: DataFrame 列表
        """
        if not filepath or not os.path.exists(filepath):
            logger.warning(f"PDF 文件不存在: {filepath}")
            return []

        tables = []

        try:
            import pdfplumber

            with pdfplumber.open(filepath) as pdf:
                logger.info(f"PDF 总页数: {len(pdf.pages)}")

                for i, page in enumerate(pdf.pages):
                    try:
                        # 尝试提取表格
                        page_tables = page.extract_tables()

                        if page_tables:
                            for table in page_tables:
                                if table and len(table) > 1:
                                    # 第一行作为表头
                                    df = pd.DataFrame(table[1:], columns=table[0])
                                    if not df.empty:
                                        tables.append(df)
                                        logger.info(f"第 {i+1} 页解析到表格，行数: {len(df)}")
                        else:
                            # 没有表格，尝试提取文本（保底方案）
                            text = page.extract_text()
                            if text:
                                logger.debug(f"第 {i+1} 页无表格，提取到文本片段")

                    except Exception as e:
                        logger.warning(f"第 {i+1} 页解析失败: {e}")

            logger.info(f"PDF 解析完成，共 {len(tables)} 个表格")
            return tables

        except ImportError:
            logger.error("pdfplumber 未安装，请执行: pip install pdfplumber")
            return []
        except Exception as e:
            logger.error(f"PDF 解析失败 [{filepath}]: {e}")
            return []

    @staticmethod
    def extract_text(filepath):
        """
        提取 PDF 全部文本内容（保底方案：无表格时提取文本）

        Args:
            filepath: PDF 文件路径

        Returns:
            str: 提取的文本内容
        """
        if not filepath or not os.path.exists(filepath):
            return ""

        try:
            import pdfplumber

            full_text = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text.append(text)

            return "\n".join(full_text)

        except Exception as e:
            logger.error(f"PDF 文本提取失败 [{filepath}]: {e}")
            return ""

    @staticmethod
    def is_scanned_pdf(filepath):
        """
        简单判断是否为扫描型 PDF（图片型，难以直接提取文字）

        Args:
            filepath: PDF 文件路径

        Returns:
            bool: 是否为扫描型PDF
        """
        try:
            import pdfplumber

            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        return False  # 有较多文字，不是扫描型
                return True  # 几乎无文字，可能是扫描型
        except Exception:
            return False
