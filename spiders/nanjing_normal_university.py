# -*- coding: utf-8 -*-
"""
南京师范大学本科招生网爬虫

【重要说明】
由于高校官网页面结构可能随时变化，以下代码为模板实现。
实际使用前，请：
1. 打开南京师范大学本科招生网，确认录取分数栏目实际URL
2. 使用浏览器开发者工具（F12）查看文章列表的HTML结构
3. 根据实际结构修改下面的 CSS 选择器

南京师范大学本科招生网参考地址：
- 首页: https://bkzs.njnu.edu.cn/
- 历年分数线栏目可能需要手动查找确认
"""

from spiders.base_spider import BaseSpider
from utils.logger import get_logger

logger = get_logger(__name__)


class NanjingNormalUniversitySpider(BaseSpider):
    """南京师范大学爬虫"""

    def __init__(self):
        super().__init__("nanjing_normal")

    def discover_score_pages(self):
        """
        发现南京师范大学录取分数相关页面
        """
        entry_url = self.school_config.get("score_entry_url", "")
        if not entry_url:
            logger.warning("南京师范大学 score_entry_url 未配置，请在 config.py 中填写")
            return []

        logger.info(f"南京师范大学 - 访问录取分数入口: {entry_url}")

        html = self.request.get_text(entry_url)
        if not html:
            return []

        links = self.html_parser.extract_links(html, base_url=entry_url)

        score_pages = []
        keywords = self.school_config.get("article_title_keywords", ["录取", "分数线", "分数"])

        for link in links:
            title = link["text"]
            href = link["href"]

            if any(kw in title for kw in keywords):
                score_pages.append({"url": href, "title": title})
                logger.info(f"发现页面: {title}")

        # 去重
        seen = set()
        unique = [p for p in score_pages if not (p["url"] in seen or seen.add(p["url"]))]

        logger.info(f"南京师范大学 - 共发现 {len(unique)} 个相关页面")
        return unique

    def parse_page(self, html, url):
        """
        解析南京师范大学招生页面
        """
        if not html:
            return []

        table_selector = self.school_config.get("table_selector", None)
        tables = self.html_parser.parse_tables(html, table_selector=table_selector)

        all_data = []
        for df in tables:
            if df.empty:
                continue
            from utils.text_cleaner import standardize_dataframe
            records = standardize_dataframe(df, self.school_name, url)
            all_data.extend(records)

        logger.info(f"南京师范大学 - 从 {url} 解析到 {len(all_data)} 条记录")
        return all_data
