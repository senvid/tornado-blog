#!/usr/bin/env python
# -*- coding:utf-8 -*-


# mysql sync connection pools wrapper around torndb


from Queue import Queue
import tinylog
import time
import torndb


log = tinylog.LogHandler("dbPool.log",logName="dbPool",level="debug")

class ConnectionPool(object):

	"""docstring for ConnectionPool"""

	def __init__(self, max_connections, connInfo):
		super(ConnectionPool, self).__init__()
		self.max_connections = max_connections
		self.connInfo = connInfo
		self._pool = Queue(max_connections)
		start = time.time()
		for x in xrange(max_connections):
			self.fillPool()

		timeDelta = (time.time() - start)*1000
		log.info("init over use:%sms" % timeDelta)

	def createConn(self, connInfo):
		try:
			# conn = MySQLdb.connect(
			    # user='blog', passwd='blog', host='localhost', port=3306, db='test')
			return torndb.Connection(**connInfo)
		except Exception, e:
			raise e

	def fillPool(self):
		try:
			conn = self.createConn(self.connInfo)
			self._pool.put(conn)
			log.info("fill conn success")
		except Exception, e:
			raise e
			
	def getConn(self):
		try:
			return self._pool.get()
		except Exception, e:
			raise e

	# notice here
	def closeConn(self, conn):
		try:
			# self._pool.get().close()
			# self.fillPool()
			self._pool.put(conn)
			#release conn
			del conn
		except Exception, e:
			raise e
	def closeAll(self):
		for x in xrange(self._pool.qsize()):
			self._pool.get().close()
		log.info("closeAll")

	def get(self, *args, **kwarguments):
		try:
			one = self.getConn()
		    return one.get(*args, **kwarguments)
		except Exception, e:
			raise e
		finally:
			self._pool.put(one)
	def makefunc(self,method,*args,**kwarguments):
		try:
			conn = self.getConn()
			log.info("get one conn  %s" % conn)
			return getattr(conn,method)(*args,**kwarguments)
		except Exception, e:
			raise e
		finally:
			self._pool.put(conn)
			log.info("release connect to pools")
connMeta ={
    "user":'blog', 
    "password":'blog',
    "host":'localhost:3306',
    "database":'test',
    "time_zone":"+8:00"
}


dbPool = ConnectionPool(5,connMeta)
raw_input(">>")
conn1 = dbPool.get("select * from tags where tag_id=20")
for i in conn1:
	print i

raw_input(">>")
conn2 = dbPool.get("select tag_type from tags where tag_id=20")
for i in conn1:
	print i

raw_input(">>")
# c = conn1.cursor()
# print c
# sql = "self * from tags"
# r = c.execute(sql)
# r = c.fetchall()
# raw_input(">>")
# conn2 = dbPool.getConn()
# c2 = conn2.cursor()
# print c2
# r2 = c2.execute(sql)
# r2 = c2.fetchall()

dbPool.closeAll()


