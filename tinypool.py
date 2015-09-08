#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
mysql sync connection pool wrapper around torndb

usage:
	import tinypool
	
	connMeta = {
	    "user": 'username',
	    "password": 'password',
	    "host": 'localhost:3306',
	    "database": 'test',
	    "time_zone": "+0:00"
	}
	db = tinypool.Pool(5, connMeta)
	res = db.get("select * from test")
'''

from Queue import Queue
import time
import torndb

# set log file
import tinylog
log = tinylog.LogHandler("dbPool.log", logName="dbPool", level="debug")
# use logging not tinylog
if not hasattr(log, "info"):
    import logging as log


class Pool(object):

    """docstring for Pool"""

    def __init__(self, max_connections, connInfo):

        self.max_connections = max_connections
        self.connInfo = connInfo
        self._pool = Queue(max_connections)
        start = time.time()
        for x in xrange(max_connections):
            self._fillPool()

        timeDelta = (time.time() - start)*1000
        log.info("db Pool init over use:%sms" % timeDelta)

    def _createConn(self, connInfo):
        return torndb.Connection(**connInfo)

    def _fillPool(self):
        try:
            conn = self._createConn(self.connInfo)
            self._pool.put(conn)
            log.info("add conn success")
        except Exception, e:
            raise e

    def _getConn(self):
        try:
            return self._pool.get()
        except Exception, e:
            raise e

    def closeAll(self):
        """Close this pool and close all database connection."""
        if self._pool.qsize():
            for x in xrange(self._pool.qsize()):
                self._pool.get().close()

    def __del__(self):
        self.closeAll()

    def _makefunc(self, method, *args, **kwarguments):
        """
        1.to do somthing
        2.Release the current connection to the pool
        3.set the variable to null.
        """
        try:
            conn = self._getConn()
            res = getattr(conn, method)(*args, **kwarguments)
            # log.info(*args, **kwarguments)
        except Exception, e:
            raise e
        finally:
            if conn:
                self._pool.put(conn)
            conn = None
        return res

    def iter(self, *args, **kwarguments):
        return self._makefunc("iter", *args, **kwarguments)

    def query(self, *args, **kwarguments):
        return self._makefunc("query", *args, **kwarguments)

    def get(self, *args, **kwarguments):
        return self._makefunc("get", *args, **kwarguments)

    def execute(self, *args, **kwarguments):
        return self._makefunc("execute", *args, **kwarguments)

    def insert(self, *args, **kwarguments):
        # torndb.py 211-215 line insert = execute_lastrowid
        return self._makefunc("insert", *args, **kwarguments)

    def update(self, *args, **kwarguments):
        return self._makefunc("update", *args, **kwarguments)

    def executemany(self, args):
        return self._makefunc("executemany", args)

    def insertmany(self, args):
        return self._makefunc("insertmany", args)

    def updatemany(self, args):
        return self._makefunc("updatemany", args)