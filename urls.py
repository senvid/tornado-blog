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
    cookie_secret="swliOTY5NzJkYTVlMTU0OTAwMTdlNjgzMTA5M2U3OGQ5NDIxZmU3Mg16",
    login_url="/login",
    debug=True,
    autoreload=True
)


app = tornado.web.Application([
    (r"/", HomeHandler),
    (r"/page", PageHandler),
    (r"/archive", ArchiveHandler),
    (r"/feed", FeedHandler),
    (r"/toptic/([^/]+)", TopticHandler),
    (r"/compose", ComposeHandler),
    (r"/login", AuthLoginHandler),
    (r"/logout", AuthLogoutHandler),
    (r"/delete", DeleteHandler),
    (r"/pagejson", PageJsonHandler),
    (r"/test", TestHandler),
    (r"/aside", AsideJsonHandler),
    (r"/about", AboutHandler),
    (r".*", PageNoFindHandler),
], **settings)

'''
wsgi 
app = tornado.wsgi.WSGIApplication([
    (r"/", HomeHandler),
    (r"/page/(\d+)",PageHandler),
    (r"/archive", ArchiveHandler),
    (r"/feed", FeedHandler),
    (r"/entry/([^/]+)", TopticHandler),
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