-- MySQL 建表语句
-- 使用前请先创建数据库: CREATE DATABASE gaokao_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE gaokao_spider;

-- 高校录取分数线主表
CREATE TABLE IF NOT EXISTS admission_scores (
    id              INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    year            VARCHAR(10)     NOT NULL COMMENT '年份，如 2024、2025',
    school_name     VARCHAR(100)    NOT NULL COMMENT '学校名称，如 苏州大学',
    province        VARCHAR(50)     DEFAULT '' COMMENT '省份，如 江苏、浙江',
    category        VARCHAR(50)     DEFAULT '' COMMENT '科类，如 物理类、历史类、综合改革、理工、文史',
    batch           VARCHAR(50)     DEFAULT '' COMMENT '批次，如 本科一批、本科批、提前批',
    major_name      VARCHAR(200)    DEFAULT '' COMMENT '专业名称',
    min_score       VARCHAR(20)     DEFAULT '' COMMENT '最低分',
    max_score       VARCHAR(20)     DEFAULT '' COMMENT '最高分',
    avg_score       VARCHAR(20)     DEFAULT '' COMMENT '平均分',
    min_rank        VARCHAR(30)     DEFAULT '' COMMENT '最低位次/排名',
    source_url      TEXT            COMMENT '数据来源页面URL',
    crawl_time      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '数据抓取时间',

    INDEX idx_year (year),
    INDEX idx_school (school_name),
    INDEX idx_province (province),
    INDEX idx_category (category),
    INDEX idx_school_year (school_name, year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='高校录取分数线采集数据表';


-- 爬虫运行日志表（可选，用于记录每次爬取任务）
CREATE TABLE IF NOT EXISTS crawl_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    school_name     VARCHAR(100)    NOT NULL COMMENT '学校名称',
    start_time      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    end_time        DATETIME        NULL COMMENT '结束时间',
    status          VARCHAR(20)     DEFAULT 'running' COMMENT '状态: running/success/failed',
    total_records   INT             DEFAULT 0 COMMENT '采集记录数',
    error_msg       TEXT            COMMENT '错误信息',
    INDEX idx_school_time (school_name, start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='爬虫运行日志';
