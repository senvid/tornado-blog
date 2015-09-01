#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado
import tornado.web
import tornado.ioloop
import tornado.autoreload
from tornado.options import define, options
from urls import app

define("port", default=8000, help="run on the given port", type=int)
define("mysql_host", default="localhost:3306", help="database host")
define("mysql_database", default="test", help="database name")
define("mysql_user", default="blog", help="database user")
define("mysql_password", default="blog", help="database password")


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app.listen(options.port)
    loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(loop)
    print 'server start..'
    loop.start()
