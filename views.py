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
            "SELECT * FROM posts ORDER BY id DESC LIMIT %s", sp
        )
        count_items = self.db.get("SELECT count(*) FROM posts")

        if count_items["count(*)"] % sp == 0:
            sumPage = count_items["count(*)"] / sp
        else:
            sumPage = count_items["count(*)"] / sp + 1
        if not articles:
            self.redirect("/compose")
            return
        self.render("home.html", articles=articles, sumPage=sumPage)

class EntryModule(tornado.web.UIModule):

    def render(self, article=None):
        return self.render_string("modules/entry.html", article=article)


class ArticleModule(tornado.web.UIModule):

    def render(self, article=None):
        return self.render_string("modules/article.html", article=article)


class AsideModule(tornado.web.UIModule, BaseHandler):

    #def render(self, getAllTags, aside_title)
    def render(self):
        getAllTags = self.db.query(
            "SELECT COUNT(id),tag_type FROM tags LEFT JOIN posts "
            "ON tag_id = article_tag_id WHERE id IS NOT NULL GROUP BY tag_id"
        )
        aside_title = self.db.query(
            "SELECT title,slug FROM posts ORDER BY id DESC LIMIT 5"
        )
        return self.render_string(
            "modules/aside.html", getAllTags=getAllTags, aside_title=aside_title
        )


class AsideJsonHandler(BaseHandler):

    def get(self):
        aside_title = self.db.query(
            "SELECT title,slug FROM posts ORDER BY id DESC LIMIT 5"
        )
        self.write(json.dumps(aside_title))


class PageHandler(BaseHandler):

    def get(self):
        try:
            page = self.get_argument("page", 1)
            if int(page) > 0:
                page_start = int(page) * sp - sp
                articles = self.db.query(
                    "SELECT * FROM posts ORDER BY id "
                    "DESC LIMIT %s,%s" % (page_start, sp)
                )
                count_items = self.db.get("SELECT count(*) FROM posts")
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
                "SELECT * FROM posts ORDER BY id DESC LIMIT %s, %s",
                page_start, sp
            )
            if not articles:
                raise tornado.web.HTTPError(404)
            self.write(json.dumps(articles, cls=Tojson))


class TestHandler(BaseHandler):

    def get(self):
        getAllTags = self.db.query(
            "SELECT COUNT(id),tag_type FROM tags LEFT JOIN posts "
            "ON tag_id = article_tag_id WHERE id IS NOT NULL GROUP BY tag_id"
        )
        self.write(str(getAllTags))


class TopicHandler(BaseHandler):

    def get(self, slug):
        nextEntry = self.get_argument("next", None)
        if nextEntry == "y":
            article = self.db.get(
                "SELECT * FROM posts WHERE id < (SELECT id FROM posts "
                "WHERE slug = %s) ORDER BY id DESC LIMIT 1", slug)
        else:
            article = self.db.get(
                "SELECT * FROM posts WHERE slug = %s", slug)
        if not article:
            self.redirect("/")
            return
        self.render("topic.html", article=article)


class ArchiveHandler(BaseHandler):

    def get(self):
        articles = self.db.query(
            "SELECT title,published,slug FROM posts ORDER BY id DESC"
        )
        self.render("archive.html", articles=articles)


class FeedHandler(BaseHandler):

    def get(self):
        articles = self.db.query(
            "SELECT * FROM posts ORDER BY id DESC LIMIT 10"
        )
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", articles=articles)




class ComposeHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        article = None
        if id:
            article = self.db.get(
                "SELECT * FROM posts LEFT JOIN tags ON "
                "article_tag_id = tag_id WHERE id = %s", id
            )
        tags = self.db.query("SELECT * FROM tags")
        self.render("compose.html", article=article, tags=tags)

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        content = self.get_argument("content")
        # tag not id
        article_tag = self.get_argument("article_tag", None)
        article_tag_id = None
        if article_tag:
            get_tag = self.db.get(
                "SELECT * FROM tags WHERE tag_type =%s", article_tag
            )
            if get_tag:
                article_tag_id = str(get_tag["tag_id"])
            else:
                get_tag = self.db.execute(
                    "INSERT INTO tags(tag_type) values(%s);SELECT @@IDENTITY",
                    article_tag
                )
                # notice here different
                article_tag_id = str(get_tag)
        if title and content:
            if id:
                article = self.db.get(
                    "SELECT * FROM posts WHERE id = %s", id
                )
                if not article:
                    raise tornado.web.HTTPError(404)
                    return
                slug = article.slug
                self.db.execute(
                    "UPDATE posts SET title = %s, content = %s,"
                    "article_tag_id = %s WHERE id = %s",
                    title, content, article_tag_id, id
                )
            else:
                today = time.strftime("%Y%m%d")
                max = self.db.get(
                    "SELECT id FROM posts ORDER BY id DESC LIMIT 1")
                max_id = max["id"]
                if not max_id:
                    max_id = 100
                slug = "".join([today, str(max_id)])
                self.db.execute(
                    "INSERT INTO posts (article_uid, title, slug, content,"
                    "article_tag_id, published) VALUES (%s,%s,%s,%s,"
                    "%s,UTC_TIMESTAMP())",
                    self.current_user.uid, title, slug, content, article_tag_id
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

    tornado.web.asynchronous
    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)

        if email and password:
            author_uid = self.db.get(
                "SELECT uid FROM users WHERE email = %s and password = %s",
                email, password
            )
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
                "DELETE FROM posts WHERE title = %s and slug = %s ",
                title_t, slug_s.split("/")[2])
            self.write("deleted")

class TagArchiveHandler(BaseHandler):
   
   def get(self, tag):
        entries = self.db.query(
            "SELECT title,slug,published FROM posts INNER JOIN tags ON "
            "article_tag_id=tag_id WHERE tag_type=%s", tag
        )
        if not entries:
               self.write_error(404)
               return   
        self.render("archive.html", articles=entries)

class SearchHandler(BaseHandler):

    def get(self):
        args = self.get_argument("search",None)
        if args:
            # sql  escape
            args = "%%%s%%" % args
            res = self.db.query(
                "SELECT title, slug,published FROM posts WHERE title LIKE "
                "%s OR content LIKE %s",args,args
            )
            self.render("archive.html",articles=res)