# -*- coding: utf-8 -*-
"""
HTML 表格解析模块
支持使用 pandas.read_html 和 BeautifulSoup 两种方式解析网页中的表格
"""

import io
import pandas as pd
from bs4 import BeautifulSoup
from utils.logger import get_logger

logger = get_logger(__name__)


class HTMLParser:
    """HTML 解析器"""

    @staticmethod
    def parse_tables(html_text, table_selector=None):
        """
        解析 HTML 中的所有表格

        Args:
            html_text: HTML 文本内容
            table_selector: CSS 选择器，用于定位特定表格（可选）

        Returns:
            list: DataFrame 列表
        """
        if not html_text:
            logger.warning("HTML 内容为空，无法解析表格")
            return []

        tables = []

        try:
            # 方式1：使用 pandas.read_html（自动识别所有表格）
            if table_selector is None:
                dfs = pd.read_html(io.StringIO(html_text))
                for df in dfs:
                    if not df.empty:
                        tables.append(df)
                logger.info(f"使用 pandas 解析到 {len(tables)} 个表格")
                return tables

            # 方式2：使用 BeautifulSoup + pandas（按选择器定位）
            soup = BeautifulSoup(html_text, "lxml")
            selected_tables = soup.select(table_selector)

            for table in selected_tables:
                try:
                    # 使用 io.StringIO 明确告诉 pandas 这是字符串内容，不是文件路径
                    df = pd.read_html(io.StringIO(str(table)))[0]
                    if not df.empty:
                        tables.append(df)
                except Exception as e:
                    logger.warning(f"解析选定表格失败: {e}")

            logger.info(f"使用选择器 [{table_selector}] 解析到 {len(tables)} 个表格")
            return tables

        except Exception as e:
            logger.error(f"HTML 表格解析失败: {e}")
            return []

    @staticmethod
    def extract_links(html_text, base_url=""):
        """
        提取页面中的所有链接

        Args:
            html_text: HTML 文本
            base_url: 基础URL，用于拼接相对链接

        Returns:
            list: 链接字典列表，每个包含 text 和 href
        """
        if not html_text:
            return []

        soup = BeautifulSoup(html_text, "lxml")
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            text = a_tag.get_text(strip=True)

            # 拼接相对URL
            if base_url and not href.startswith(("http://", "https://", "//")):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            elif href.startswith("//"):
                href = "https:" + href

            links.append({"text": text, "href": href})

        return links

    @staticmethod
    def extract_title(html_text):
        """
        提取网页标题

        Args:
            html_text: HTML 文本

        Returns:
            str: 网页标题
        """
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "lxml")
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else ""
