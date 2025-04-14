import logging
import sys
from os import path

import nonebot
from nonebot.log import logger

import config
import xiuXian.plugins.xiuxian_config as xiuxian_config

if __name__ == '__main__':

    if len(sys.argv) != 5 or sys.argv[1] != '-PORT' or sys.argv[3] != '-GROUP':
        print("Usage: python3 main.py -PORT <port_number> -GROUP <group_id>")
        sys.exit(1)

    config.PORT = int(sys.argv[2])

    xiuxian_config.group_id = int(sys.argv[4])

    nonebot.init(config)
    logger.setLevel(logging.WARN)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'xiuXian', 'plugins'),
        'xiuXian.plugins'
    )
    nonebot.get_bot()
    nonebot.run()
