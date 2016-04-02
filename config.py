#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.options import define, options
import tinypool


define("port", default=8000, help="run on the given port", type=int)
define("mysql_host", default="localhost:3306", help="database host")
define("mysql_database", default="test", help="database name")
define("mysql_user", default="blog", help="database user")
define("mysql_password", default="blog", help="database password")


dbConfig = {
    "host": options.mysql_host,
    "database": options.mysql_database,
    "user": options.mysql_user,
    "password": options.mysql_password,
    "time_zone": "+8:00"
}

pool = tinypool.Pool(5, dbConfig)
