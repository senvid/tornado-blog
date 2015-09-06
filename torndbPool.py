#!/usr/bin/env python
# -*- coding:utf-8 -*-


# mysql sync connection pools

import MySQLdb
from Queue import Queue


class ConnectionPool(object):

	"""docstring for ConnectionPool"""

	def __init__(self, max_connections, connInfo):
		super(ConnectionPool, self).__init__()
		self.max_connections = max_connections
		self.connInfo = connInfo
		self._pool = Queue(self.max_connections)

		for x in xrange(self.max_connections):
			self.fillPool()
		print "初始化。。  ",self._pool.queue

	def createConn(self, connInfo):
		try:
			# conn = MySQLdb.connect(
			    # user='blog', passwd='blog', host='localhost', port=3306, db='test')
			conn = MySQLdb.connect(**connInfo)
			conn.info = "pool"
		    conn.ping()

		except Exception, e:
			raise e

	def fillPool(self):
		try:
			connDB = self.createConn(self.connInfo)
			self._pool.put(connDB)
			print "fill    ",connDB
		except Exception, e:
			raise e
			
	def getConn(self):
		try:
			one = self._pool.get()
			print "get one .. ",one
			return one
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
		for x in xrange self._pool.qsize():
			self._pool.get().close()
		print "closeAll"

connMeta ={
    "user":'blog', 
    "passwd":'blog',
    "host":'localhost', 
    "port":3306,
    "db":'test'
}


dbPool = ConnectionPool(5,connMeta)
conn1 = dbPool.getConn()
c = conn1.cursor()
print c
sql = "self * from tags"
r = c.execute(sql)
r = c.fetchall()
raw_input(">>")
conn2 = dbPool.getConn()
c2 = conn2.cursor()
print c2
r2 = c2.execute(sql)
r2 = c2.fetchall()

dbPool.closeAll()