#!/usr/bin/env python
# coding:utf-8

# JSON serializable
# example:
#d= [{'t':datetime.datetime.now(),"a":2}]
#r = json.dumps(d,cls=Tojson)


import json
import datetime
import decimal


class Tojson(json.JSONEncoder):

    def ddate(self, d):
        date_attr = [d.year, d.month, d.day]
        if isinstance(d, datetime.datetime):
            date_attr.extend(
                [d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
        return datetime.datetime(*date_attr)

    def dtime(self, d):
        return datetime.date(d.year, d.month, d.day)

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            d = self.ddate(obj)
            # return d.strftime("%Y-%m-%d %H:%M:%S")
            return d.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.date):
            d = self.dtime(obj)
            return d.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M:%S")
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return super(Tojson, self).default(obj)
