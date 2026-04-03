import os
from multiprocessing import Process

from biz.utils.log import logger


def handle_queue(function: callable, data: any, token: str, url: str, url_slug: str):
    # 确保所有参数都是字符串类型，避免multiprocessing传递时出现bytes类型问题
    token = str(token)
    url = str(url)
    url_slug = str(url_slug)
    
    process = Process(target=function, args=(data, token, url, url_slug))
    process.start()
