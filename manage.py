#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado
import tornado.web
import tornado.ioloop
import tornado.autoreload
import tornado.options

import logging
from urls import app
import config
from datetime import datetime


if __name__ == "__main__":
    # python manage.py --port=8000
    tornado.options.parse_command_line()
    app.listen(config.options.port)
    loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.add_reload_hook(config.pool.closeAll)
    # 新版本已自动开启
    # tornado.autoreload.start(loop, 1000)
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info('************  server start at %s ************' % start_time)
    loop.start()
