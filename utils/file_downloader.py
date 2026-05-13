# -*- coding: utf-8 -*-
"""
文件下载模块
用于下载高校官网的 Excel、PDF 等附件
"""

import os
import urllib.parse
from config import RAW_DIR, ATTACHMENT_KEYWORDS
from utils.request_utils import RequestUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class FileDownloader:
    """文件下载器"""

    def __init__(self, raw_dir=None):
        self.raw_dir = raw_dir or RAW_DIR
        os.makedirs(self.raw_dir, exist_ok=True)
        self.request = RequestUtils()

    def is_attachment_url(self, url):
        """
        判断URL是否为附件链接

        Args:
            url: 链接地址

        Returns:
            bool: 是否为附件
        """
        if not url:
            return False
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in ATTACHMENT_KEYWORDS)

    def get_filename_from_url(self, url, response=None):
        """
        从URL或响应头中提取文件名

        Args:
            url: 下载链接
            response: HTTP响应对象（可选）

        Returns:
            str: 文件名
        """
        # 尝试从响应头获取
        if response and "Content-Disposition" in response.headers:
            cd = response.headers["Content-Disposition"]
            if "filename=" in cd:
                filename = cd.split("filename=")[-1].strip('"\'')
                return urllib.parse.unquote(filename)

        # 从URL路径获取
        parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed.path)
        if filename:
            return urllib.parse.unquote(filename)

        # 默认文件名
        return "downloaded_file"

    def download(self, url, school_name="", sub_dir=""):
        """
        下载文件

        Args:
            url: 下载链接
            school_name: 学校名称（用于分类存储）
            sub_dir: 子目录

        Returns:
            str: 保存的本地文件路径，失败返回空字符串
        """
        if not url:
            return ""

        # 构建保存目录
        save_dir = self.raw_dir
        if school_name:
            save_dir = os.path.join(save_dir, school_name)
        if sub_dir:
            save_dir = os.path.join(save_dir, sub_dir)
        os.makedirs(save_dir, exist_ok=True)

        try:
            logger.info(f"开始下载文件: {url}")
            response = self.request.get(url, stream=True)
            if not response:
                logger.error(f"下载失败（无响应）: {url}")
                return ""

            filename = self.get_filename_from_url(url, response)
            # 如果文件名没有扩展名，尝试从Content-Type推断
            if "." not in filename:
                content_type = response.headers.get("Content-Type", "")
                if "excel" in content_type or "spreadsheet" in content_type:
                    filename += ".xlsx"
                elif "pdf" in content_type:
                    filename += ".pdf"

            # 避免文件名重复，添加序号
            filepath = os.path.join(save_dir, filename)
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(filepath):
                filepath = os.path.join(save_dir, f"{base_name}_{counter}{ext}")
                counter += 1

            # 保存文件
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"文件下载成功: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"下载异常 [{url}]: {e}")
            return ""

    def close(self):
        """关闭请求会话"""
        self.request.close()
