# -*- coding: utf-8 -*-
"""
MySQL 数据库写入模块
将采集的数据保存到 MySQL 数据库
"""

from config import MYSQL_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)


class MySQLWriter:
    """MySQL 写入器"""

    def __init__(self, config=None):
        self.config = config or MYSQL_CONFIG
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        连接 MySQL 数据库

        Returns:
            bool: 连接是否成功
        """
        try:
            import pymysql

            self.connection = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset=self.config["charset"],
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.cursor = self.connection.cursor()
            logger.info("MySQL 连接成功")
            return True

        except ImportError:
            logger.error("pymysql 未安装，请执行: pip install pymysql")
            return False
        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            return False

    def insert(self, data, table_name="admission_scores"):
        """
        插入数据到数据库

        Args:
            data: 数据字典列表
            table_name: 表名

        Returns:
            int: 插入的记录数
        """
        if not data:
            return 0

        if not self.connection:
            if not self.connect():
                return 0

        columns = [
            "year", "school_name", "province", "category", "batch",
            "major_name", "min_score", "max_score", "avg_score",
            "min_rank", "source_url", "crawl_time",
        ]

        placeholders = ", ".join(["%s"] * len(columns))
        column_str = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"

        count = 0
        for record in data:
            try:
                values = [record.get(col, "") for col in columns]
                self.cursor.execute(sql, values)
                count += 1
            except Exception as e:
                logger.warning(f"单条插入失败: {e}")

        try:
            self.connection.commit()
            logger.info(f"MySQL 插入成功: {count} 条记录")
        except Exception as e:
            logger.error(f"MySQL 提交失败: {e}")
            self.connection.rollback()

        return count

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("MySQL 连接已关闭")
