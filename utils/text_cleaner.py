# -*- coding: utf-8 -*-
"""
文本清洗与数据标准化模块
"""

import re
from datetime import datetime
from config import CATEGORY_MAP
from utils.logger import get_logger

logger = get_logger(__name__)


class TextCleaner:
    """文本清洗类"""

    @staticmethod
    def clean_text(text):
        """
        清洗文本：去除空白字符、换行符等

        Args:
            text: 原始文本

        Returns:
            str: 清洗后的文本
        """
        if text is None:
            return ""
        text = str(text)
        # 去除各种空白字符
        text = re.sub(r"\s+", " ", text)
        # 去除不可见字符
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", text)
        return text.strip()

    @staticmethod
    def extract_year(text):
        """
        从文本中提取年份

        Args:
            text: 包含年份的文本

        Returns:
            str: 4位年份，如 "2024"，未找到返回 ""
        """
        if not text:
            return ""
        # 匹配 20xx 年份
        match = re.search(r"20\d{2}", str(text))
        if match:
            return match.group()
        return ""

    @staticmethod
    def extract_number(text):
        """
        从文本中提取数字（用于分数、位次等）

        Args:
            text: 包含数字的文本

        Returns:
            str: 提取的数字字符串，未找到返回 ""
        """
        if text is None:
            return ""
        text = str(text)
        # 匹配整数或小数
        match = re.search(r"\d+\.?\d*", text.replace(",", "").replace("，", ""))
        if match:
            return match.group()
        return ""

    @staticmethod
    def standardize_category(text):
        """
        标准化科类名称

        Args:
            text: 原始科类文本

        Returns:
            str: 标准化后的科类名称
        """
        if not text:
            return ""
        text = str(text).strip()
        for key, value in CATEGORY_MAP.items():
            if key in text:
                return value
        return text

    @staticmethod
    def standardize_province(text):
        """
        标准化省份名称

        Args:
            text: 原始省份文本

        Returns:
            str: 标准化后的省份名称
        """
        if not text:
            return ""
        text = str(text).strip()
        # 去除末尾的"省"、"市"字样（保留直辖市）
        if text.endswith("省"):
            text = text[:-1]
        # 常见的省份名称修正
        province_map = {
            "北京": "北京", "天津": "天津", "上海": "上海", "重庆": "重庆",
            "河北": "河北", "山西": "山西", "辽宁": "辽宁", "吉林": "吉林",
            "黑龙江": "黑龙江", "江苏": "江苏", "浙江": "浙江", "安徽": "安徽",
            "福建": "福建", "江西": "江西", "山东": "山东", "河南": "河南",
            "湖北": "湖北", "湖南": "湖南", "广东": "广东", "海南": "海南",
            "四川": "四川", "贵州": "贵州", "云南": "云南", "陕西": "陕西",
            "甘肃": "甘肃", "青海": "青海", "台湾": "台湾", "内蒙古": "内蒙古",
            "广西": "广西", "西藏": "西藏", "宁夏": "宁夏", "新疆": "新疆",
        }
        for key, value in province_map.items():
            if key in text:
                return value
        return text

    @staticmethod
    def is_score_related(text):
        """
        判断文本是否与录取分数相关

        Args:
            text: 文本内容

        Returns:
            bool: 是否相关
        """
        from config import SCORE_KEYWORDS
        if not text:
            return False
        text = str(text)
        return any(keyword in text for keyword in SCORE_KEYWORDS)

    @staticmethod
    def get_crawl_time():
        """
        获取当前抓取时间

        Returns:
            str: 格式化的时间字符串
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def standardize_dataframe(df, school_name, source_url):
    """
    将原始DataFrame标准化为统一格式

    Args:
        df: pandas DataFrame（原始表格数据）
        school_name: 学校名称
        source_url: 数据来源URL

    Returns:
        list: 标准化后的字典列表
    """
    results = []
    cleaner = TextCleaner()
    crawl_time = cleaner.get_crawl_time()

    # 列名映射：将常见列名映射为标准列名
    # 注意：更具体的（更长的）关键词应该排在前面，避免"专业"先于"专业名称"被匹配
    column_mapping = {
        # 年份
        "年份": "year", "年度": "year", "年": "year",
        # 省份（包含苏州大学特有的"省/市/区"格式）
        "省/市/区": "province", "省份": "province", "省市": "province", "地区": "province",
        # 科类
        "科类": "category", "类别": "category", "科目": "category",
        "类型": "category", "文理": "category",
        # 批次
        "录取批次": "batch", "批次": "batch",
        # 专业组/选科/备注
        "专业组/选科/备注": "major_group", "选科": "major_group", "备注": "major_group",
        # 专业（注意：更长的关键词放在前面，避免子串误匹配）
        "专业名称": "major_name", "招生专业": "major_name",
        "专业名": "major_name", "专业": "major_name",
        # 最低分
        "录取最低分": "min_score", "最低录取分": "min_score",
        "投档最低分": "min_score", "最低分": "min_score",
        # 最高分
        "录取最高分": "max_score", "最高分": "max_score",
        # 平均分
        "录取平均分": "avg_score", "平均分": "avg_score",
        # 最低位次
        "最低位次": "min_rank", "最低排名": "min_rank",
        "位次": "min_rank", "排名": "min_rank",
    }

    # 重命名列
    df.columns = [str(col).strip() for col in df.columns]
    renamed_columns = {}

    # 按关键词长度降序遍历，确保"专业名称"先于"专业"被匹配，避免子串冲突
    sorted_mapping = sorted(column_mapping.items(), key=lambda x: len(x[0]), reverse=True)

    for col in df.columns:
        # 跳过已处理的列（避免一个列被多次匹配）
        if col in renamed_columns:
            continue
        for cn_key, en_key in sorted_mapping:
            if cn_key in col:
                renamed_columns[col] = en_key
                break

    df = df.rename(columns=renamed_columns)

    # 遍历每一行，构建标准数据
    for _, row in df.iterrows():
        record = {
            "province": "",
            "major_name": "",
            "major_group": "",
            "max_score": "",
            "min_score": "",
            "avg_score": "",
        }

        # 填充数据
        for key in record.keys():
            if key in df.columns:
                value = row[key]
                if key in ["min_score", "max_score", "avg_score"]:
                    record[key] = cleaner.extract_number(value)
                elif key == "province":
                    record[key] = cleaner.standardize_province(value)
                else:
                    record[key] = cleaner.clean_text(value)

        results.append(record)

    return results
