# -*- coding: utf-8 -*-
"""
项目全局配置文件
"""

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")

# 请求配置
REQUEST_CONFIG = {
    "timeout": 30,           # 请求超时时间（秒）
    "max_retries": 3,        # 最大重试次数
    "retry_delay": 2,        # 重试间隔（秒）
    "request_interval": 1.5, # 每次请求间隔（秒），遵守爬取礼仪
}

# User-Agent 列表，随机轮换
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

# 录取相关关键词，用于判断页面是否包含录取数据
SCORE_KEYWORDS = [
    "录取分数", "录取分数线", "历年录取", "分省分专业",
    "录取情况", "录取结果", "招生录取", "投档线",
    "最低分", "最高分", "平均分", "位次", "录取查询",
    "分专业录取", "各省录取", "录取统计", "录取数据",
]

# 附件关键词，用于识别下载链接
ATTACHMENT_KEYWORDS = [
    ".xls", ".xlsx", ".pdf", ".doc", ".docx", ".zip", ".rar",
]

# MySQL 数据库配置（预留，按需填写）
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "gaokao_spider",
    "charset": "utf8mb4",
}

# 目标学校配置
# 注意：以下URL和选择器需要根据各学校官网实际结构调整
SCHOOL_CONFIGS = {
    "suzhou": {
        "name": "苏州大学",
        "home_url": "https://zsb.suda.edu.cn/",
        # 录取分数栏目入口URL，需要用户根据实际情况填写或修改
        "score_entry_url": "https://zsb.suda.edu.cn/search.aspx?text=2025%E5%B9%B4%E4%B8%8A%E6%B5%B7%E5%90%84%E4%B8%93%E4%B8%9A%E5%BD%95%E5%8F%96%E5%88%86%E6%95%B0%E4%B8%80%E8%A7%88%E8%A1%A8&nf=2025&province=%E4%B8%8A%E6%B5%B7",
        # CSS选择器，用于定位录取相关文章列表中的链接
        # 需要根据实际页面结构修改
        "article_list_selector": "#ctl00_ContentPlaceHolder1_GridView1 a",
        # 文章标题中匹配录取分数的关键词
        "article_title_keywords": ["省/市/区", "专业名称", "专业组/选科/备注","最高分","最低分","平均分"],
        # 数据表格选择器
        # 苏州大学数据表格有特定ID，精确选择可避免解析到布局表格
        "table_selector": "#ctl00_ContentPlaceHolder1_GridView1",
    },
    "ocean": {
        "name": "中国海洋大学",
        "home_url": "https://bkzs.ouc.edu.cn/",
        "score_entry_url": "https://bkzs.ouc.edu.cn/lnlqfs/list.htm",
        "article_list_selector": "ul.news_list li a",
        "article_title_keywords": ["录取分数", "录取分数线", "历年录取", "分省分专业"],
        "table_selector": "table",
    },
    "nanjing_normal": {
        "name": "南京师范大学",
        "home_url": "https://bkzs.njnu.edu.cn/",
        "score_entry_url": "https://bkzs.njnu.edu.cn/main.htm",
        "article_list_selector": "ul.news-list li a",
        "article_title_keywords": ["录取分数", "录取分数线", "历年录取", "分省分专业"],
        "table_selector": "table",
    },
}

# 科类标准化映射
CATEGORY_MAP = {
    "物理类": "物理类",
    "历史类": "历史类",
    "综合改革": "综合改革",
    "理工": "理工",
    "理工类": "理工",
    "文史": "文史",
    "文史类": "文史",
    "文科": "文史",
    "理科": "理工",
    "物理": "物理类",
    "历史": "历史类",
    "综合": "综合改革",
    "3+3综合": "综合改革",
    "3+1+2": "综合改革",
    "本科批": "本科批",
    "本科一批": "本科一批",
    "本科二批": "本科二批",
    "提前批": "提前批",
}

# 输出CSV文件列顺序
# 根据需求自定义：这里只保留省/市/区、专业名称、平均分
# 如需更多字段，取消注释下方完整版
OUTPUT_COLUMNS = [
    "province", "major_name", "major_group", "max_score", "min_score", "avg_score",
]

# CSV中文表头映射
CSV_HEADERS = {
    "province": "省份",
    "major_name": "专业",
    "major_group": "选科备注",
    "max_score": "最高分",
    "min_score": "最低分",
    "avg_score": "平均分",
}

# 完整字段版本（如需使用，注释上方简版，取消注释下方）：
# OUTPUT_COLUMNS = [
#     "year", "school_name", "province", "category", "batch",
#     "major_name", "min_score", "max_score", "avg_score",
#     "min_rank", "source_url", "crawl_time",
# ]
