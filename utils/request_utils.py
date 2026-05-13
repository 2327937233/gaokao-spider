# -*- coding: utf-8 -*-
"""
网络请求工具模块
封装 requests 请求，支持重试、超时、User-Agent 轮换、请求间隔等
"""

import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import REQUEST_CONFIG, USER_AGENTS
from utils.logger import get_logger

logger = get_logger(__name__)


class RequestUtils:
    """请求工具类"""

    def __init__(self):
        self.session = requests.Session()
        self.timeout = REQUEST_CONFIG.get("timeout", 30)
        self.max_retries = REQUEST_CONFIG.get("max_retries", 3)
        self.retry_delay = REQUEST_CONFIG.get("retry_delay", 2)
        self.request_interval = REQUEST_CONFIG.get("request_interval", 1.5)

        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self):
        """生成随机请求头"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def get(self, url, **kwargs):
        """
        发送 GET 请求

        Args:
            url: 请求URL
            **kwargs: 其他 requests 参数

        Returns:
            requests.Response: 响应对象，失败返回 None
        """
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            logger.debug(f"请求 URL: {url}")
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            # 遵守请求间隔
            time.sleep(self.request_interval)
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败 [{url}]: {e}")
            return None

    def get_text(self, url, **kwargs):
        """
        获取网页文本内容

        Args:
            url: 请求URL
            **kwargs: 其他参数

        Returns:
            str: 网页文本，失败返回空字符串
        """
        response = self.get(url, **kwargs)
        if response:
            return response.text
        return ""

    def get_binary(self, url, **kwargs):
        """
        获取二进制内容（用于下载文件）

        Args:
            url: 请求URL
            **kwargs: 其他参数

        Returns:
            bytes: 二进制内容，失败返回 None
        """
        response = self.get(url, **kwargs)
        if response:
            return response.content
        return None

    def check_robots_txt(self, base_url):
        """
        检查 robots.txt（简单实现）

        Args:
            base_url: 网站根URL

        Returns:
            bool: 是否允许爬取（当前简化处理，始终返回True，建议实际使用时完善）
        """
        # TODO: 实际项目中可完善 robots.txt 解析逻辑
        logger.info(f"robots.txt 检查（简化）: {base_url}")
        return True

    def close(self):
        """关闭 session"""
        self.session.close()
