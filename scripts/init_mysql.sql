-- MySQL数据库初始化脚本
-- 创建代码审查数据库表结构

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS tb_ai_code_review CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用tb_ai_code_review数据库
USE tb_ai_code_review;

-- 创建合并请求审核日志表
CREATE TABLE IF NOT EXISTS mr_review_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    source_branch VARCHAR(255) NOT NULL,
    target_branch VARCHAR(255) NOT NULL,
    updated_at BIGINT NOT NULL,
    commit_messages TEXT,
    score INT,
    url TEXT,
    review_result TEXT,
    additions INT DEFAULT 0,
    deletions INT DEFAULT 0,
    last_commit_id VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_updated_at (updated_at),
    INDEX idx_project_author (project_name(100), author(100)),
    INDEX idx_created_at (created_at),
    INDEX idx_composite (project_name(100), author(100), updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建推送审核日志表
CREATE TABLE IF NOT EXISTS push_review_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    branch VARCHAR(255) NOT NULL,
    updated_at BIGINT NOT NULL,
    commit_messages TEXT,
    score INT,
    review_result TEXT,
    additions INT DEFAULT 0,
    deletions INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_updated_at (updated_at),
    INDEX idx_project_author (project_name(100), author(100)),
    INDEX idx_created_at (created_at),
    INDEX idx_composite (project_name(100), author(100), updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 输出创建结果
SELECT 'MySQL数据库表结构初始化完成' as status;