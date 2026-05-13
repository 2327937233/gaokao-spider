# -*- coding: utf-8 -*-
"""
爬虫模块
包含基类和各学校的具体爬虫实现
"""

from spiders.base_spider import BaseSpider
from spiders.suzhou_university import SuzhouUniversitySpider
from spiders.ocean_university import OceanUniversitySpider
from spiders.nanjing_normal_university import NanjingNormalUniversitySpider

# 爬虫注册表，用于 main.py 根据名称选择爬虫
SPIDER_REGISTRY = {
    "suzhou": SuzhouUniversitySpider,
    "ocean": OceanUniversitySpider,
    "nanjing_normal": NanjingNormalUniversitySpider,
}

__all__ = [
    "BaseSpider",
    "SuzhouUniversitySpider",
    "OceanUniversitySpider",
    "NanjingNormalUniversitySpider",
    "SPIDER_REGISTRY",
]