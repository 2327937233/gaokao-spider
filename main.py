# -*- coding: utf-8 -*-
"""
高校录取分数线采集系统 - 入口程序

使用方法:
    python main.py --school suzhou
    python main.py --school ocean
    python main.py --school nanjing_normal
    python main.py --school all          # 爬取所有学校

参数说明:
    --school    指定学校代号，可选值: suzhou, ocean, nanjing_normal, all
    --output    输出方式，可选值: csv (默认), mysql, both
"""

import argparse
import sys
import os

# 将项目根目录加入 Python 路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from spiders import SPIDER_REGISTRY
from storage.csv_writer import CSVWriter
from storage.mysql_writer import MySQLWriter
from utils.logger import get_logger

logger = get_logger(__name__)


def run_spider(school_key, output_mode="csv"):
    """
    运行指定学校的爬虫

    Args:
        school_key: 学校代号
        output_mode: 输出方式: csv / mysql / both

    Returns:
        list: 采集的数据
    """
    spider_class = SPIDER_REGISTRY.get(school_key)
    if not spider_class:
        logger.error(f"未知学校代号: {school_key}，可用选项: {', '.join(SPIDER_REGISTRY.keys())}")
        return []

    spider = spider_class()
    results = spider.run()

    if not results:
        logger.warning(f"[{school_key}] 未采集到任何数据")
        return []

    # 输出到 CSV
    if output_mode in ("csv", "both"):
        csv_writer = CSVWriter()
        csv_writer.write(results, filename=f"{school_key}_scores.csv")

    # 输出到 MySQL
    if output_mode in ("mysql", "both"):
        mysql_writer = MySQLWriter()
        mysql_writer.insert(results)
        mysql_writer.close()

    return results


def run_all_spiders(output_mode="csv"):
    """
    运行所有学校的爬虫

    Args:
        output_mode: 输出方式

    Returns:
        list: 所有学校采集的数据汇总
    """
    all_results = []

    for school_key in SPIDER_REGISTRY.keys():
        logger.info(f"\n{'='*60}")
        logger.info(f"开始爬取学校: {school_key}")
        logger.info(f"{'='*60}")

        try:
            results = run_spider(school_key, output_mode=output_mode)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"爬取 [{school_key}] 时发生异常: {e}")

    # 汇总输出
    if all_results and output_mode in ("csv", "both"):
        csv_writer = CSVWriter()
        csv_writer.write(all_results, filename="all_schools_scores.csv")

    logger.info(f"\n{'='*60}")
    logger.info(f"全部爬取完成，总计 {len(all_results)} 条数据")
    logger.info(f"{'='*60}")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="高校录取分数线采集系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例命令:
  python main.py --school suzhou              # 爬取苏州大学
  python main.py --school ocean               # 爬取中国海洋大学
  python main.py --school nanjing_normal      # 爬取南京师范大学
  python main.py --school all                 # 爬取所有学校
  python main.py --school suzhou --output csv   # 仅输出 CSV（默认）
  python main.py --school all --output both     # 同时输出 CSV 和 MySQL
        """
    )

    parser.add_argument(
        "--school",
        type=str,
        required=True,
        help=f"学校代号，可选: {', '.join(SPIDER_REGISTRY.keys())}, 或 all"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="csv",
        choices=["csv", "mysql", "both"],
        help="输出方式: csv(默认), mysql, both"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("高校录取分数线采集系统启动")
    logger.info("=" * 60)

    if args.school == "all":
        run_all_spiders(output_mode=args.output)
    else:
        run_spider(args.school, output_mode=args.output)

    logger.info("程序执行完毕")


if __name__ == "__main__":
    main()
