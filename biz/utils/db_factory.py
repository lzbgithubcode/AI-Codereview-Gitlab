"""
数据库连接工厂
支持SQLite和MySQL两种数据库，默认使用MySQL
"""
import os
import sqlite3
import logging
from contextlib import contextmanager

try:
    import pymysql
except ImportError:
    pymysql = None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DBConnectionFactory:
    """数据库连接工厂类"""
    
    @staticmethod
    def get_db_type():
        """获取数据库类型，默认使用mysql"""
        return os.environ.get('DATABASE_TYPE', 'mysql').lower()
    
    @staticmethod
    @contextmanager
    def get_connection():
        """获取数据库连接"""
        db_type = DBConnectionFactory.get_db_type()
        
        if db_type == 'mysql':
            # MySQL连接（默认）
            if pymysql is None:
                logger.error("❌ MySQL连接失败: pymysql模块未安装")
                raise ImportError("pymysql模块未安装，请运行: pip install PyMySQL")
            
            try:
                host = os.environ.get('MYSQL_HOST', 'localhost')
                port = int(os.environ.get('MYSQL_PORT', '3306'))
                database = os.environ.get('MYSQL_DB', 'codereview')
                user = os.environ.get('MYSQL_USER', 'root')
                
                logger.info(f"🔗 正在连接MySQL数据库: {user}@{host}:{port}/{database}")
                
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=os.environ.get('MYSQL_PASSWORD', ''),
                    charset='utf8mb4'
                )
                
                # 测试连接是否成功
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                
                logger.info("✅ MySQL数据库连接成功")
                
                try:
                    yield conn
                finally:
                    conn.close()
                    logger.info("🔌 MySQL数据库连接已关闭")
                    
            except Exception as e:
                logger.error(f"❌ MySQL数据库连接失败: {e}")
                raise
                
        else:
            # 使用SQLite
            db_file = os.environ.get('SQLITE_DB_FILE', 'data/data.db')
            
            try:
                logger.info(f"🔗 正在连接SQLite数据库: {db_file}")
                
                conn = sqlite3.connect(db_file)
                
                # 测试连接是否成功
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                logger.info("✅ SQLite数据库连接成功")
                
                try:
                    yield conn
                finally:
                    conn.close()
                    logger.info("🔌 SQLite数据库连接已关闭")
                    
            except Exception as e:
                logger.error(f"❌ SQLite数据库连接失败: {e}")
                raise
    
    @staticmethod
    def execute_sql(sql, params=None):
        """执行SQL语句"""
        db_type = DBConnectionFactory.get_db_type()
        
        if db_type == 'mysql':
            # MySQL参数占位符转换
            sql = sql.replace('?', '%s')
        
        with DBConnectionFactory.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor
    
    @staticmethod
    def fetch_all(sql, params=None):
        """查询所有记录"""
        cursor = DBConnectionFactory.execute_sql(sql, params)
        return cursor.fetchall()
    
    @staticmethod
    def fetch_one(sql, params=None):
        """查询单条记录"""
        cursor = DBConnectionFactory.execute_sql(sql, params)
        return cursor.fetchone()