#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado
import tornado.web
import tornado.ioloop
import tornado.autoreload
from tornado.options import options
import logging
from urls import app
import config



if __name__ == "__main__":
    tornado.options.parse_command_line()
    app.listen(config.options.port)
    loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.add_reload_hook(config.pool.closeAll)
    tornado.autoreload.start(loop,1000)
    logging.info('**************  server start  **************')
    loop.start()
