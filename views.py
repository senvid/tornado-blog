#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado
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
    
# articles per page
sp = 3


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        self.conn = torndb.Connection(
            host=options.mysql_host,
            database=options.mysql_database,
            user=options.mysql_user,
            password=options.mysql_password,
            time_zone='+8:00'
        )
        return self.conn

    def get_current_user(self):
        user_id = self.get_secure_cookie("blog_user")
        if not user_id:
            return None
        return self.db.get("SELECT * FROM users WHERE uid = %s", int(user_id))

    def write_error(self, status_code, **kwargs):
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
        articles = self.db.query(
            "SELECT * FROM articles ORDER BY id DESC LIMIT %s", sp
        )
        count_items = self.db.get("SELECT count(*) FROM articles")
        if count_items["count(*)"] % sp == 0:
            sumPage = count_items["count(*)"] / sp
        else:
            sumPage = count_items["count(*)"] / sp + 1
        if not articles:
            self.redirect("/compose")
            return
        self.render("home.html", articles=articles, sumPage=sumPage)


class AsideJsonHandler(BaseHandler):

    def get(self):
        aside_title = self.db.query(
            "SELECT title,slug FROM articles ORDER BY id DESC LIMIT 5"
        )
        self.write(json.dumps(aside_title))


class PageHandler(BaseHandler):

    def get(self):
        try:
            page = self.get_argument("page", 1)
            if int(page) > 0:
                page_start = int(page) * sp - sp
                articles = self.db.query(
                    "SELECT * FROM articles ORDER BY id "
                    "DESC LIMIT %s,%s" % (page_start, sp)
                )
                count_items = self.db.get("SELECT count(*) FROM articles")
                if count_items["count(*)"] % sp == 0:
                    sumPage = count_items["count(*)"] / sp
                else:
                    sumPage = count_items["count(*)"] / sp + 1
                if not articles:
                    raise tornado.web.HTTPError(404)
                self.render("home.html", articles=articles, sumPage=sumPage)
            else:
                self.redirect("/")
        except:
            # self.redirect("/")
            self.write("NO PAGE FOUND")


class PageJsonHandler(BaseHandler):

    def get(self):
        page = self.get_argument("page", None)
        if page:
            page_start = int(page) * sp - sp
           # articles = self.db.query("SELECT * FROM articles ORDER BY published "
            #            "DESC LIMIT %s,5" , page_start)
            articles = self.db.query(
                "SELECT * FROM articles ORDER BY id DESC LIMIT %s, %s", page_start, sp
            )
            if not articles:
                raise tornado.web.HTTPError(404)
            self.write(json.dumps(articles, cls=Tojson))


class TestHandler(BaseHandler):

    def get(self):
        argus = self.get_argument("t", None)
        if argus:
            self.write(argus)
        else:
            self.write("nothing")


class TopicHandler(BaseHandler):

    def get(self, slug):
        nextEntry = self.get_argument("next", None)
        if nextEntry == "y":
            article = self.db.get(
                "SELECT * FROM articles WHERE id < (SELECT id FROM articles "
                "WHERE slug = %s) ORDER BY id DESC LIMIT 1", slug)
        else:
            article = self.db.get(
                "SELECT * FROM articles WHERE slug = %s", slug)
        if not article:
            self.redirect("/")
            return
        self.render("topic.html", article=article)


class ArchiveHandler(BaseHandler):

    def get(self):
        articles = self.db.query(
            "SELECT title,published,slug FROM articles ORDER BY id DESC"
        )
        self.render("archive.html", articles=articles)


class FeedHandler(BaseHandler):

    def get(self):
        articles = self.db.query(
            "SELECT * FROM articles ORDER BY id DESC LIMIT 10"
        )
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", articles=articles)


class EntryModule(tornado.web.UIModule):

    def render(self, article):
        return self.render_string("modules/entry.html", article=article)


class ArticleModule(tornado.web.UIModule):

    def render(self, article):
        return self.render_string("modules/article.html", article=article)


class AsideModule(tornado.web.UIModule):

    def render(self):
        return self.render_string("modules/aside.html")


class ComposeHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        article = None
        if id:
            article = self.db.get(
                "SELECT * FROM articles WHERE id = %s", int(id))
        self.render("compose.html", article=article)

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        content = self.get_argument("content")
        if title and content:
            if id:
                article = self.db.get(
                    "SELECT * FROM articles WHERE id = %s", int(id)
                )
                if not article:
                    raise tornado.web.HTTPError(404)
                slug = article.slug
                self.db.execute(
                    "UPDATE articles SET title = %s, content = %s"
                    "WHERE id = %s", title, content, int(id)
                )
            else:
                today = time.strftime("%Y%m%d")
                # max = self.db.get("SELECT MAX(id) FROM articles")
                # max_id = max["MAX(id)"]
                max = self.db.get(
                    "SELECT id FROM articles ORDER BY id DESC LIMIT 1")
                max_id = max["id"]
                if not max_id:
                    max_id = 100
                slug = "".join([today, str(max_id)])

                # while True:
                #     e = self.db.get(
                #         "SELECT id FROM articles WHERE slug = %s", slug)
                #     if not e:
                #         break
                #     slug += "-2"
                self.db.execute(
                    "INSERT INTO articles (article_uid,title,slug,content,"
                    "published) VALUES (%s,%s,%s,%s,UTC_TIMESTAMP())",
                    self.current_user.uid, title, slug, content
                )
            self.redirect("/topic/" + slug)
        else:
            self.write("Please enter a valid title and content")


class AuthLoginHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        if self.get_secure_cookie("blog_user"):
            self.redirect("/")
            return
        else:
            mytoken = binascii.b2a_hex(os.urandom(16))
            self.set_cookie("_xsrf", mytoken)
        self.render("login.html")

    # tornado.web.asynchronous
    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)

        if email and password:
            author_uid = self.db.get(
                "SELECT uid FROM users WHERE email = %s and password = %s", email, password)
            if author_uid:
                self.set_secure_cookie("blog_user", str(author_uid['uid']))
                # self.redirect("/")
                self.write("ok")
            else:
                self.write("false")
        else:
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
        title_t = self.get_argument("title", None)
        slug_s = self.get_argument("slug", None)
        if title_t and slug_s:
            self.db.execute(
                "DELETE FROM articles WHERE title = %s and slug = %s ",
                title_t, slug_s.split("/")[2])
            self.write("deleted")

