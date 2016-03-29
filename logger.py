#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@version: 1.0.0
@author: zheng guang
@contact: zg.zhu@daocloud.io
@time: 16/3/5 上午9:33
"""
import logging


def __init_logger__():
    # 创建一个logger
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # 给logger添加handler
    logger.addHandler(ch)
    # 记录一条日志
    return logger

logger=__init_logger__()


if __name__ == '__main__':
    pass