#!/usr/bin/env python3
"""
MySQL数据库表初始化脚本
确保AI审查结果能够正确写入数据库
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('conf/.env')

from biz.utils.db_factory import DBConnectionFactory

def init_mysql_tables():
    """初始化MySQL表结构"""
    print("🚀 开始初始化MySQL数据库表结构...")
    
    try:
        with DBConnectionFactory.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建mr_review_log表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mr_review_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_name VARCHAR(255),
                    author VARCHAR(255),
                    source_branch VARCHAR(255),
                    target_branch VARCHAR(255),
                    updated_at BIGINT,
                    commit_messages TEXT,
                    score INT,
                    url TEXT,
                    review_result TEXT,
                    additions INT DEFAULT 0,
                    deletions INT DEFAULT 0,
                    last_commit_id VARCHAR(255) DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建push_review_log表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS push_review_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_name VARCHAR(255),
                    author VARCHAR(255),
                    branch VARCHAR(255),
                    updated_at BIGINT,
                    commit_messages TEXT,
                    score INT,
                    review_result TEXT,
                    additions INT DEFAULT 0,
                    deletions INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引（兼容MySQL语法）
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'mr_review_log' 
                AND index_name = 'idx_mr_review_log_updated_at'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute('CREATE INDEX idx_mr_review_log_updated_at ON mr_review_log (updated_at)')
            
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'push_review_log' 
                AND index_name = 'idx_push_review_log_updated_at'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute('CREATE INDEX idx_push_review_log_updated_at ON push_review_log (updated_at)')
            
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'mr_review_log' 
                AND index_name = 'idx_mr_review_log_commit'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute('CREATE INDEX idx_mr_review_log_commit ON mr_review_log (last_commit_id)')
            
            conn.commit()
            print("✅ MySQL数据库表结构初始化成功")
            
            # 验证表结构
            cursor.execute("SHOW TABLES LIKE 'mr_review_log'")
            mr_exists = cursor.fetchone()
            cursor.execute("SHOW TABLES LIKE 'push_review_log'")
            push_exists = cursor.fetchone()
            
            print(f"mr_review_log表: {'✅ 存在' if mr_exists else '❌ 不存在'}")
            print(f"push_review_log表: {'✅ 存在' if push_exists else '❌ 不存在'}")
            
            return True
            
    except Exception as e:
        print(f"❌ MySQL表结构初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_table_data():
    """检查表数据"""
    print("\n📊 检查数据库表数据...")
    
    try:
        with DBConnectionFactory.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查mr_review_log表数据
            cursor.execute("SELECT COUNT(*) FROM mr_review_log")
            mr_count = cursor.fetchone()[0]
            
            # 检查push_review_log表数据
            cursor.execute("SELECT COUNT(*) FROM push_review_log")
            push_count = cursor.fetchone()[0]
            
            print(f"mr_review_log表记录数: {mr_count}")
            print(f"push_review_log表记录数: {push_count}")
            
            # 如果有数据，显示最新记录
            if mr_count > 0:
                cursor.execute("SELECT project_name, author, updated_at FROM mr_review_log ORDER BY id DESC LIMIT 3")
                print("最新mr_review_log记录:")
                for row in cursor.fetchall():
                    print(f"  - {row[0]} by {row[1]} at {row[2]}")
            
            if push_count > 0:
                cursor.execute("SELECT project_name, author, updated_at FROM push_review_log ORDER BY id DESC LIMIT 3")
                print("最新push_review_log记录:")
                for row in cursor.fetchall():
                    print(f"  - {row[0]} by {row[1]} at {row[2]}")
                    
    except Exception as e:
        print(f"❌ 检查表数据失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("📋 MySQL数据库表结构初始化")
    print("=" * 60)
    
    # 初始化表结构
    if init_mysql_tables():
        check_table_data()
        
        print("\n🎯 下一步操作:")
        print("✅ 表结构已初始化完成")
        print("✅ 现在AI审查结果将正确写入MySQL数据库")
        print("✅ 请重启服务以应用更改")
    
    print("=" * 60)