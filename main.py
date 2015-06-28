#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado
import tornado.web
import tornado.ioloop
import tornado.autoreload
from datetimeTojson import Tojson
from tornado.options import define, options
import time
import json
import logging
import os.path
import re
import binascii
import hashlib
try:
    import torndb
except ImportError:
    logging.warn("no module named torndb")
try:
    import markdown
except ImportError:
    logging.warn("no module named markdown")

define("port", default=8000, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="blog database host")
define("mysql_database", default="blog", help="blog database name")
define("mysql_user", default="blog", help="blog database user")
define("mysql_password", default="blog", help="blog database password")
#每页显示多少文章
sp = 3

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        self.conn = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)
        return self.conn

    def get_current_user(self):
        user_id = self.get_secure_cookie("blog_user")
        if not user_id: return None
        return self.db.get("SELECT * FROM users WHERE id = %s", int(user_id))

    def write_error(self,status_code,**kwargs):
        if status_code == 404:
            self.render("404.html")
        elif status_code == 500:
            self.render('500.html')
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)
            
class PageNoFindHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("404.html")

class HomeHandler(BaseHandler):
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY id "
                                "DESC LIMIT %s",sp)
        count_id = self.db.get("SELECT count(id) FROM entries;")
        if count_id["count(id)"] % sp == 0:
            sumPage = count_id["count(id)"] / sp
        else:
            sumPage = count_id["count(id)"] / sp + 1
        if not entries:
            self.redirect("/compose")
            return
        self.render("home.html", entries=entries,sumPage=sumPage)

class AsideJsonHandler(BaseHandler):
    def get(self):
        aside_title = self.db.query("SELECT title,slug FROM entries ORDER BY id "
                                    "DESC LIMIT 6")
        self.write(json.dumps(aside_title))

class PageHandler(BaseHandler):
    def get(self):
        try:         
            page_num = self.get_argument("page_num",1)
            if int(page_num) > 0:
                page_start = int(page_num) * sp - sp
                entries = self.db.query("SELECT * FROM entries ORDER BY id "
                            "DESC LIMIT %s,%s" % (page_start,sp))
                count_id = self.db.get("SELECT count(id) FROM entries;")
                if count_id["count(id)"] % sp == 0:
                    sumPage = count_id["count(id)"] / sp
                else:
                    sumPage = count_id["count(id)"] / sp + 1
                if not entries: raise tornado.web.HTTPError(404)
                self.render("home.html",entries=entries,sumPage=sumPage)
            else:self.redirect("/")
        except:           
            #self.redirect("/")
            self.write("NO PAGE FOUND")

class PageJsonHandler(BaseHandler):
    def get(self):
        page_num = self.get_argument("page_num",None)
        if page_num:
            page_start = int(page_num) * sp - sp
           # entries = self.db.query("SELECT * FROM entries ORDER BY published " 
            #            "DESC LIMIT %s,5" , page_start)
            entries = self.db.query("SELECT slug,title,id,published,html  FROM entries ORDER BY id " 
                        "DESC LIMIT %s,%s" % (page_start,sp))
            if not entries: raise tornado.web.HTTPError(404)         
            self.write(json.dumps(entries,cls=Tojson))

class EntryHandler(BaseHandler):
    def get(self, slug):
        entry = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        if not entry: raise tornado.web.HTTPError(404)
        self.render("entry.html", entry=entry)

class ArchiveHandler(BaseHandler):
    def get(self):
        entries = self.db.query("SELECT title,published,slug FROM entries ORDER BY id "
                                "DESC")
        self.render("archive.html", entries=entries)

class FeedHandler(BaseHandler):
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY id "
                                "DESC LIMIT 10")
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", entries=entries)

class EntryModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)

class ComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        entry = None
        if id:
            entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
        self.render("compose.html", entry=entry)

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        text = self.get_argument("markdown")
        html = markdown.markdown(text)
        if title and text:  
            if id:
                entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
                if not entry: raise tornado.web.HTTPError(404)
                slug = entry.slug
                self.db.execute(
                    "UPDATE entries SET title = %s, markdown = %s, html = %s "
                    "WHERE id = %s", title, text, html, int(id))
            else:
                '''
                slug = unicodedata.normalize("NFKD", title).encode(
                    "ascii", "ignore")
                slug = re.sub(r"[^\w]+", " ", slug)
                slug = "-".join(slug.lower().strip().split())
                if not slug: slug = "entry"
                '''
                today =time.strftime("%Y%m%d")
                max =self.db.get("SELECT MAX(id) FROM entries")
                #单行查询用get 多行用query。get不允许查询多行 否则引发异常
                #前者返回一个字典 后者返回一个包含字典的列表，每行为一个字典
                #此处返回的对象格式是{'MAX(id)': 23L}

                max_id = max["MAX(id)"]
                if not max_id : max_id = 100
                slug = "-".join([today,str(max_id)])
                while True:
                    e = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
                    if not e: break
                    slug += "-2"
                self.db.execute(
                    "INSERT INTO entries (author_id,title,slug,markdown,html,"
                    "published) VALUES (%s,%s,%s,%s,%s,UTC_TIMESTAMP())",
                    self.current_user.id, title, slug, text, html)
            self.redirect("/entry/" + slug)
        else: self.write("Please enter a valid content")

class AuthLoginHandler(BaseHandler):
 
    @tornado.web.asynchronous
    def get(self):
        if self.get_secure_cookie("blog_user"):
            self.redirect("/")
            return
        else:           
            mytoken = binascii.b2a_hex(os.urandom(16))
            self.set_cookie("_xsrf",mytoken)
        self.render("login.html")
    
    #@tornado.web.asynchronous
    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)
        
        if email and password:
            author_id = self.db.get("SELECT id FROM users WHERE email = %s and password = %s", email, password)
            #返回一个字典 例如:{'id':1}
            if author_id:
                self.set_secure_cookie("blog_user", str(author_id['id']))
                #self.redirect("/")
                self.write("ok")
                return
            else:
                self.write("false")
        else :
            self.write("false")

class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("blog_user")
        self.redirect("/")
        
class AboutHandler(BaseHandler):
    def get(self):
        self.render("about.html")
        
class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        title_t = self.get_argument("title",None)
        slug_s = self.get_argument("slug",None)
        if title_t and slug_s:
            self.db.execute(
                "DELETE FROM entries WHERE title = %s and slug = %s ", 
                title_t, slug_s.split("/")[2])
            self.write("deleted")

settings = dict(
    blog_title=u"Blog",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    ui_modules={"Entry": EntryModule},
    xsrf_cookies=True,
    cookie_secret="swliOTY5NzJkYTVlMTU0OTAwMTdlNjgzMTA5M2U3OGQ5NDIxZmU3Mg16",
    login_url="/login",
    debug=True,
    autoreload=True
)
'''
wsgi相关 已废弃
app = tornado.wsgi.WSGIApplication([
    (r"/", HomeHandler),
    (r"/page/(\d+)",PageHandler),
    (r"/archive", ArchiveHandler),
    (r"/feed", FeedHandler),
    (r"/entry/([^/]+)", EntryHandler),
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

app = tornado.web.Application([
    (r"/", HomeHandler),
    (r"/page", PageHandler),
    (r"/archive", ArchiveHandler),
    (r"/feed", FeedHandler),
    (r"/entry/([^/]+)", EntryHandler),
    (r"/compose", ComposeHandler),
    (r"/login", AuthLoginHandler),
    (r"/logout", AuthLogoutHandler),
    (r"/delete",DeleteHandler),
    (r"/test",PageJsonHandler),
    (r"/aside",AsideJsonHandler),
    (r"/about",AboutHandler),
    (r".*",PageNoFindHandler),
],**settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app.listen(options.port)
    loop = tornado.ioloop.IOLoop.instance()

    tornado.autoreload.start(loop)
    loop.start()

