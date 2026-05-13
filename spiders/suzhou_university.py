# -*- coding: utf-8 -*-
"""
苏州大学本科招生网爬虫

【关键设计说明】
苏州大学招生网的录取数据页面是"查询结果页"结构：
- 访问一个带参数的 search.aspx 页面
- 页面直接展示数据表格（如2025年山东省各专业录取分数）
- 页面上没有"文章列表→文章详情"的层级结构

因此本爬虫重写了 discover_score_pages()：
不再提取文章链接，而是直接把 score_entry_url 当作数据页面返回，
由 parse_page() 直接解析页面中的表格。
"""

from spiders.base_spider import BaseSpider
from utils.logger import get_logger

logger = get_logger(__name__)


class SuzhouUniversitySpider(BaseSpider):
    """苏州大学爬虫"""

    def __init__(self):
        super().__init__("suzhou")

    def discover_score_pages(self):
        """
        发现苏州大学录取分数相关页面

        苏州大学招生网为查询结果页结构，直接展示表格数据。
        本方法将配置的 score_entry_url 或 score_entry_urls 作为数据页面返回。
        """
        # 支持单URL字符串（score_entry_url）或多URL列表（score_entry_urls）
        entry_urls = self.school_config.get("score_entry_urls", [])
        if not entry_urls:
            single_url = self.school_config.get("score_entry_url", "")
            if single_url:
                entry_urls = [single_url]

        if not entry_urls:
            logger.warning("苏州大学 score_entry_url / score_entry_urls 未配置，请在 config.py 中填写")
            return []

        pages = []
        for i, url in enumerate(entry_urls):
            logger.info(f"苏州大学 - 数据查询页 {i+1}: {url}")
            pages.append({"url": url, "title": f"苏州大学录取数据查询页-{i+1}"})

        return pages

    def parse_page(self, html, url):
        """
        解析苏州大学招生页面中的表格数据

        苏州大学查询结果页通常包含一个 GridView 表格，
        列可能包括：省/市/区、专业名称、最低分、最高分、平均分 等
        """
        if not html:
            logger.warning("【调试】html 为空，无法解析")
            return []

        # 【调试】打印HTML前1000字符，确认页面内容
        logger.info(f"【调试】获取到HTML，长度: {len(html)} 字符")
        logger.info(f"【调试】HTML前500字符: {html[:500]}")

        # 使用配置中的表格选择器，默认提取页面所有表格
        table_selector = self.school_config.get("table_selector", None)
        logger.info(f"【调试】使用表格选择器: {table_selector}")

        tables = self.html_parser.parse_tables(html, table_selector=table_selector)
        logger.info(f"【调试】pandas.read_html 解析到 {len(tables)} 个表格")

        all_data = []
        for i, df in enumerate(tables):
            logger.info(f"【调试】表格 {i+1}: 形状 {df.shape}, 列: {list(df.columns)}")
            if df.empty:
                logger.info(f"【调试】表格 {i+1} 为空，跳过")
                continue

            # 打印表格前3行用于调试
            logger.info(f"【调试】表格 {i+1} 前3行:\n{df.head(3).to_string()}")

            from utils.text_cleaner import standardize_dataframe
            records = standardize_dataframe(df, self.school_name, url)
            logger.info(f"【调试】表格 {i+1} 标准化后得到 {len(records)} 条记录")
            all_data.extend(records)

        logger.info(f"苏州大学 - 从 {url} 解析到 {len(all_data)} 条记录")
        return all_data
