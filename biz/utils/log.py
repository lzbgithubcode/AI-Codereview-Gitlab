import logging
import os
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# 加载环境变量（兼容正式环境使用 .env.dist）
env_file = "conf/.env" if os.path.exists("conf/.env") else "conf/.env.dist"
load_dotenv(env_file)

# 自定义 Logger 类，重写 warn 和 error 方法
class CustomLogger(logging.Logger):
    def warn(self, msg, *args, **kwargs):
        # 在 warn 消息前添加 ⚠️
        msg_with_emoji = f"⚠️ {msg}"
        super().warning(msg_with_emoji, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        # 在 error 消息前添加 ❌
        msg_with_emoji = f"❌ {msg}"
        super().error(msg_with_emoji, *args, **kwargs)


# 日志目录
log_dir = os.environ.get("LOG_DIR", "log")

# 确保日志目录存在
os.makedirs(log_dir, exist_ok=True)

# 获取当前日期用于文件名
today = datetime.now().strftime('%Y-%m-%d')

# 普通日志（按日期轮转，每天一个文件）
log_file = os.environ.get("LOG_FILE", f"{log_dir}/app_{today}.log")
log_backup_count = int(os.environ.get("LOG_BACKUP_COUNT", 30))  # 默认保留30天
# 设置日志级别
log_level = os.environ.get("LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level.upper(), logging.INFO)

# 普通日志处理器（按日期轮转）
file_handler = TimedRotatingFileHandler(
    filename=log_file,
    when='midnight',  # 每天午夜轮转
    interval=1,
    backupCount=log_backup_count,
    encoding='utf-8',
    atTime=None
)
# 重命名文件名中的日期变量
file_handler.namer = lambda filename: filename.replace('.log', f'_{datetime.now().strftime("%Y-%m-%d")}.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'))
file_handler.setLevel(LOG_LEVEL)

# 错误日志处理器（单独记录ERROR级别日志）
error_log_file = os.environ.get("ERROR_LOG_FILE", f"{log_dir}/error_{today}.log")
error_file_handler = TimedRotatingFileHandler(
    filename=error_log_file,
    when='midnight',
    interval=1,
    backupCount=log_backup_count,
    encoding='utf-8',
    atTime=None
)
error_file_handler.namer = lambda filename: filename.replace('.log', f'_{datetime.now().strftime("%Y-%m-%d")}.log')
error_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'))
error_file_handler.setLevel(logging.ERROR)  # 只记录ERROR级别

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(LOG_LEVEL)


# 使用自定义的 Logger 类
logger = CustomLogger(__name__)
logger.setLevel(LOG_LEVEL)  # 设置 Logger 的日志级别
logger.addHandler(file_handler)
logger.addHandler(error_file_handler)
logger.addHandler(console_handler)
