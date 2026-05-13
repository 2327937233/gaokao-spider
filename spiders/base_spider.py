# -*- coding: utf-8 -*-
"""
爬虫基类模块
所有学校爬虫的基类，定义通用接口和流程
"""

import time
from urllib.parse import urljoin

from config import SCHOOL_CONFIGS, SCORE_KEYWORDS
from utils.request_utils import RequestUtils
from utils.text_cleaner import TextCleaner, standardize_dataframe
from utils.file_downloader import FileDownloader
from utils.logger import get_logger
from parsers.html_parser import HTMLParser
from parsers.excel_parser import ExcelParser
from parsers.pdf_parser import PDFParser
from storage.csv_writer import CSVWriter

logger = get_logger(__name__)


class BaseSpider:
    """
    高校录取分数线爬虫基类

    子类需要重写的方法：
    - discover_score_pages(): 发现录取分数相关页面URL列表
    - parse_page(html, url): 解析单个页面（如默认实现不满足需求）
    """

    def __init__(self, school_key):
        """
        初始化爬虫

        Args:
            school_key: 学校在配置中的key，如 "suzhou"
        """
        self.school_key = school_key
        self.school_config = SCHOOL_CONFIGS.get(school_key, {})
        self.school_name = self.school_config.get("name", school_key)

        self.request = RequestUtils()
        self.downloader = FileDownloader()
        self.html_parser = HTMLParser()
        self.excel_parser = ExcelParser()
        self.pdf_parser = PDFParser()
        self.csv_writer = CSVWriter()
        self.text_cleaner = TextCleaner()

        self.results = []  # 采集结果列表

        logger.info(f"爬虫初始化完成: {self.school_name} ({school_key})")

    def discover_score_pages(self):
        """
        发现录取分数相关页面URL列表
        【子类可重写此方法以适配不同学校官网结构】

        默认实现：
        1. 访问 score_entry_url
        2. 提取页面中所有链接
        3. 筛选标题包含录取关键词的链接

        Returns:
            list: 页面URL列表，每个元素为字典 {"url": str, "title": str}
        """
        entry_url = self.school_config.get("score_entry_url", "")
        if not entry_url:
            logger.warning(f"[{self.school_name}] 未配置 score_entry_url，无法自动发现页面")
            return []

        logger.info(f"[{self.school_name}] 开始发现录取分数页面，入口: {entry_url}")

        html = self.request.get_text(entry_url)
        if not html:
            return []

        # 提取所有链接
        links = self.html_parser.extract_links(html, base_url=entry_url)

        # 筛选与录取分数相关的链接
        score_pages = []
        keywords = self.school_config.get("article_title_keywords", SCORE_KEYWORDS)

        for link in links:
            title = link["text"]
            href = link["href"]

            if not title or not href:
                continue

            # 判断标题是否包含录取关键词
            if any(kw in title for kw in keywords):
                score_pages.append({"url": href, "title": title})
                logger.debug(f"发现相关页面: {title} -> {href}")

        # 去重
        seen = set()
        unique_pages = []
        for page in score_pages:
            if page["url"] not in seen:
                seen.add(page["url"])
                unique_pages.append(page)

        logger.info(f"[{self.school_name}] 发现 {len(unique_pages)} 个录取分数相关页面")
        return unique_pages

    def parse_page(self, html, url):
        """
        解析单个页面的表格数据
        【子类可重写此方法以适配不同页面结构】

        默认实现：
        1. 提取页面中的所有HTML表格
        2. 标准化数据格式
        3. 返回结构化数据

        Args:
            html: 页面HTML文本
            url: 页面URL

        Returns:
            list: 数据字典列表
        """
        if not html:
            return []

        # 使用配置中的表格选择器（如果有）
        table_selector = self.school_config.get("table_selector", None)
        tables = self.html_parser.parse_tables(html, table_selector=table_selector)

        all_data = []
        for df in tables:
            if df.empty:
                continue
            # 标准化数据
            records = standardize_dataframe(df, self.school_name, url)
            all_data.extend(records)

        logger.info(f"[{self.school_name}] 从 {url} 解析到 {len(all_data)} 条记录")
        return all_data

    def handle_attachments(self, html, base_url):
        """
        处理页面中的附件（Excel、PDF等）

        Args:
            html: 页面HTML
            base_url: 页面基础URL

        Returns:
            list: 下载的本地文件路径列表
        """
        links = self.html_parser.extract_links(html, base_url=base_url)
        downloaded_files = []

        for link in links:
            href = link["href"]
            if self.downloader.is_attachment_url(href):
                filepath = self.downloader.download(
                    href,
                    school_name=self.school_name,
                    sub_dir="attachments"
                )
                if filepath:
                    downloaded_files.append(filepath)

        return downloaded_files

    def parse_attachment(self, filepath):
        """
        解析下载的附件文件

        Args:
            filepath: 本地文件路径

        Returns:
            list: 数据字典列表
        """
        if not filepath:
            return []

        all_data = []
        lower_path = filepath.lower()

        try:
            if lower_path.endswith((".xls", ".xlsx")):
                tables = self.excel_parser.parse(filepath)
                for df in tables:
                    records = standardize_dataframe(df, self.school_name, f"file://{filepath}")
                    all_data.extend(records)

            elif lower_path.endswith(".pdf"):
                tables = self.pdf_parser.parse(filepath)
                for df in tables:
                    records = standardize_dataframe(df, self.school_name, f"file://{filepath}")
                    all_data.extend(records)

                # 如果表格解析为空，尝试文本提取（保底方案）
                if not all_data:
                    text = self.pdf_parser.extract_text(filepath)
                    if text:
                        logger.warning(f"PDF 未解析出表格，已提取文本（需手动处理）: {filepath}")

            logger.info(f"[{self.school_name}] 附件解析完成: {filepath}, 共 {len(all_data)} 条记录")

        except Exception as e:
            logger.error(f"附件解析失败 [{filepath}]: {e}")

        return all_data

    def crawl_page(self, page_info):
        """
        爬取单个页面（包括页面本身和其中的附件）

        Args:
            page_info: 页面信息字典 {"url": str, "title": str}

        Returns:
            list: 该页面采集的所有数据
        """
        url = page_info["url"]
        title = page_info.get("title", "")

        logger.info(f"[{self.school_name}] 正在爬取: {title} -> {url}")

        html = self.request.get_text(url)
        if not html:
            logger.warning(f"[{self.school_name}] 页面获取失败: {url}")
            return []
        logger.info(f"【调试】页面请求成功，HTML长度: {len(html)} 字符")

        page_data = []

        # 1. 解析页面中的表格
        table_data = self.parse_page(html, url)
        page_data.extend(table_data)

        # 2. 处理附件
        attachments = self.handle_attachments(html, url)
        for filepath in attachments:
            attachment_data = self.parse_attachment(filepath)
            page_data.extend(attachment_data)

        return page_data

    def run(self):
        """
        执行完整爬取流程

        Returns:
            list: 所有采集的数据
        """
        logger.info(f"=" * 50)
        logger.info(f"开始爬取: {self.school_name}")
        logger.info(f"=" * 50)

        self.results = []

        try:
            # 1. 发现录取分数相关页面
            pages = self.discover_score_pages()

            if not pages:
                logger.warning(f"[{self.school_name}] 未发现录取分数相关页面，请检查配置")
                return []

            # 2. 逐个爬取页面
            for page in pages:
                try:
                    page_data = self.crawl_page(page)
                    self.results.extend(page_data)
                    logger.info(f"[{self.school_name}] 当前累计采集: {len(self.results)} 条")
                except Exception as e:
                    logger.error(f"[{self.school_name}] 爬取页面异常 [{page['url']}]: {e}")

            # 3. 保存结果
            if self.results:
                self.csv_writer.write(self.results, filename=f"{self.school_key}_scores.csv")
                logger.info(f"[{self.school_name}] 爬取完成，共 {len(self.results)} 条数据")
            else:
                logger.warning(f"[{self.school_name}] 未采集到任何数据")

        except Exception as e:
            logger.error(f"[{self.school_name}] 爬取流程异常: {e}")

        finally:
            self.request.close()
            self.downloader.close()

        return self.results

    def get_results(self):
        """获取采集结果"""
        return self.results