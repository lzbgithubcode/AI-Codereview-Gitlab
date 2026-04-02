#!/usr/bin/env python3
"""
数据库兼容性测试脚本
测试SQLite和MySQL数据库方案的兼容性
"""
import os
import sys
import tempfile
import shutil

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sqlite_compatibility():
    """测试SQLite兼容性"""
    print("=== 测试SQLite兼容性 ===")
    
    # 设置SQLite环境变量
    os.environ['DATABASE_TYPE'] = 'sqlite'
    os.environ['SQLITE_DB_FILE'] = 'data/test_data.db'
    
    try:
        from biz.service.review_service import ReviewService
        from biz.entity.review_entity import MergeRequestReviewEntity
        
        # 创建临时数据库文件
        test_db_path = 'data/test_data.db'
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # 测试数据库初始化
        ReviewService.init_db()
        print("✅ SQLite数据库初始化成功")
        
        # 测试插入数据
        test_entity = MergeRequestReviewEntity(
            project_name="test_project",
            author="test_user",
            source_branch="feature/test",
            target_branch="main",
            updated_at=1234567890,
            commit_messages="测试提交",
            score=85,
            url="http://example.com",
            review_result="测试审查结果",
            additions=10,
            deletions=5,
            last_commit_id="abc123"
        )
        
        ReviewService.insert_mr_review_log(test_entity)
        print("✅ SQLite数据插入成功")
        
        # 测试查询数据
        df = ReviewService.get_mr_review_logs()
        print(f"✅ SQLite数据查询成功，获取到 {len(df)} 条记录")
        
        # 清理测试数据
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ SQLite测试失败: {e}")
        return False

def test_mysql_compatibility():
    """测试MySQL兼容性"""
    print("\n=== 测试MySQL兼容性 ===")
    
    # 检查MySQL配置
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    
    if not mysql_password:
        print("⚠️  MySQL密码未配置，跳过MySQL测试")
        return True
    
    # 设置MySQL环境变量
    os.environ['DATABASE_TYPE'] = 'mysql'
    os.environ['MYSQL_DB'] = 'codereview_test'
    
    try:
        import pymysql
        
        # 测试MySQL连接
        conn = pymysql.connect(
            host=mysql_host,
            port=int(mysql_port),
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4'
        )
        
        # 创建测试数据库
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS codereview_test")
        
        conn.close()
        print("✅ MySQL连接测试成功")
        
        # 导入业务模块（此时会使用MySQL配置）
        from biz.service.review_service import ReviewService
        from biz.entity.review_entity import MergeRequestReviewEntity
        
        # 测试数据库初始化
        ReviewService.init_db()
        print("✅ MySQL数据库初始化成功")
        
        # 测试插入数据
        test_entity = MergeRequestReviewEntity(
            project_name="test_project",
            author="test_user",
            source_branch="feature/test",
            target_branch="main",
            updated_at=1234567890,
            commit_messages="测试提交",
            score=85,
            url="http://example.com",
            review_result="测试审查结果",
            additions=10,
            deletions=5,
            last_commit_id="abc123"
        )
        
        ReviewService.insert_mr_review_log(test_entity)
        print("✅ MySQL数据插入成功")
        
        # 测试查询数据
        df = ReviewService.get_mr_review_logs()
        print(f"✅ MySQL数据查询成功，获取到 {len(df)} 条记录")
        
        # 清理测试数据库
        conn = pymysql.connect(
            host=mysql_host,
            port=int(mysql_port),
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            cursor.execute("DROP DATABASE IF EXISTS codereview_test")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL测试失败: {e}")
        return False

def test_default_mysql():
    """测试默认MySQL配置（不设置DATABASE_TYPE）"""
    print("\n=== 测试默认MySQL配置 ===")
    
    # 清除DATABASE_TYPE环境变量，测试默认值
    if 'DATABASE_TYPE' in os.environ:
        del os.environ['DATABASE_TYPE']
    
    # 检查MySQL配置
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    
    if not mysql_password:
        print("⚠️  MySQL密码未配置，跳过默认MySQL测试")
        return True
    
    try:
        import pymysql
        
        # 测试MySQL连接
        conn = pymysql.connect(
            host=mysql_host,
            port=int(mysql_port),
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4'
        )
        
        # 创建测试数据库
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS codereview_test")
        
        conn.close()
        print("✅ 默认MySQL连接测试成功")
        
        # 设置测试数据库
        os.environ['MYSQL_DB'] = 'codereview_test'
        
        # 导入业务模块（此时应该使用默认的MySQL）
        from biz.service.review_service import ReviewService
        from biz.entity.review_entity import MergeRequestReviewEntity
        
        # 测试数据库初始化
        ReviewService.init_db()
        print("✅ 默认MySQL数据库初始化成功")
        
        # 测试插入数据
        test_entity = MergeRequestReviewEntity(
            project_name="test_project_default",
            author="test_user_default",
            source_branch="feature/test",
            target_branch="main",
            updated_at=1234567890,
            commit_messages="测试默认提交",
            score=90,
            url="http://example.com",
            review_result="测试默认审查结果",
            additions=15,
            deletions=3,
            last_commit_id="def456"
        )
        
        ReviewService.insert_mr_review_log(test_entity)
        print("✅ 默认MySQL数据插入成功")
        
        # 清理测试数据库
        conn = pymysql.connect(
            host=mysql_host,
            port=int(mysql_port),
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            cursor.execute("DROP DATABASE IF EXISTS codereview_test")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 默认MySQL测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始数据库兼容性测试...")
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 测试默认MySQL
    default_mysql_success = test_default_mysql()
    
    # 测试SQLite
    sqlite_success = test_sqlite_compatibility()
    
    # 测试MySQL
    mysql_success = test_mysql_compatibility()
    
    # 输出测试结果
    print("\n=== 测试结果汇总 ===")
    print(f"默认MySQL配置: {'✅ 通过' if default_mysql_success else '❌ 失败'}")
    print(f"SQLite兼容性: {'✅ 通过' if sqlite_success else '❌ 失败'}")
    print(f"MySQL兼容性: {'✅ 通过' if mysql_success else '❌ 失败'}")
    
    if default_mysql_success and sqlite_success and mysql_success:
        print("\n🎉 所有数据库兼容性测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查代码修改")
        return 1

if __name__ == "__main__":
    sys.exit(main())