#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado
import os
from views import *

settings = dict(
    blog_title=u"Blog",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    ui_modules={
        "Entry": EntryModule,
        "Article": ArticleModule,
        "Aside": AsideModule,
    },
    xsrf_cookies=True,
    cookie_secret="sw7GpEHbTTih7NQOvGrtx05Y/1PYhkbFqiDCdY2Rgzo=",
    login_url="/login",
    debug=True,
    autoreload=True
)


app = tornado.web.Application([
    (r"/", HomeHandler),
    (r"/archive", ArchiveHandler),
    (r"/aside", AsideJsonHandler),
    (r"/about", AboutHandler),
    (r"/compose", ComposeHandler),
    (r"/delete", DeleteHandler),
    (r"/login", AuthLoginHandler),
    (r"/logout", AuthLogoutHandler),
    (r"/feed", FeedHandler),
    (r"/page", PageHandler),
    (r"/search", SearchHandler),
    # (r"/pagejson", PageJsonHandler),
    (r"/topic/([^/]+)", TopicHandler),
    (r"/tag/([^/]+)", TagArchiveHandler),
    (r"/test", TestHandler),
    (r".*", PageNoFindHandler),
], **settings)

'''
wsgi 
app = tornado.wsgi.WSGIApplication([
    (r"/", HomeHandler),
    (r"/page/(\d+)",PageHandler),
    (r"/archive", ArchiveHandler),
    (r"/feed", FeedHandler),
    (r"/entry/([^/]+)", TopicHandler),
    (r"/compose", ComposeHandler),
    (r"/login", AuthLoginHandler),
    (r"/logout", AuthLogoutHandler),
    (r"/delete",DeleteHandler),
    (r"/test",PageJsonHandler),
    (r"/aside",AsideJsonHandler),
    (r"/about",AboutHandler),
    (r".*",PageNoFindHandler),
],**settings)

def application(environ,start_response):
    return app(environ,start_response)

'''
