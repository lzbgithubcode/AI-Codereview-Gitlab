"""
API 服务主程序入口
"""
import os
from dotenv import load_dotenv

# 必须在其他导入之前加载环境变量（兼容正式环境使用 .env.dist）
env_file = "conf/.env" if os.path.exists("conf/.env") else "conf/.env.dist"
load_dotenv(env_file)

from biz.api import api_app, init_app
from biz.api.scheduler import setup_scheduler
from biz.utils.config_checker import check_config

# 初始化应用并注册路由
init_app(api_app)

if __name__ == '__main__':
    check_config()
    # 启动定时任务调度器
    setup_scheduler()

    # 启动Flask API服务
    port = int(os.environ.get('SERVER_PORT', 5001))
    api_app.run(host='0.0.0.0', port=port)
