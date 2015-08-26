##Demo仅供学习


###介绍
----
简单博客程序.

参考了tornado中的实例.


###依赖
----
* python2.7
* tornado
* torndb
* MySQL
* MySQL-python
* markdown


###使用的css js
----
- [x] jQuery v2.1.1
- [x] jquery.scrollTo-1.1.13
- [x] jsSHA/1.6.0/sha1.js
- [x] bootstrap3
- [x] ckeditor
- [x] highlight


###MySQL表结构
----
```SQL
CREATE TABLE IF NOT EXISTS users(
  uid int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  email varchar(30) NOT NULL, 
  password varchar(30) NOT NULL,
  nickname varchar(10) NOT NULL,
  INDEX email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=2;

CREATE TABLE IF NOT EXISTS tags(
  tag_id int(10) UNSIGNED NOT NULL DEFAULT NULL PRIMARY KEY AUTO_INCREMENT,
  tag_parentid int(10) UNSIGNED DEFAULT NULL,
  tag_type varchar(20) DEFAULT NULL,
  INDEX (tag_parentid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=2;

CREATE TABLE IF NOT EXISTS articles(
  id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  slug varchar(50) NOT NULL,
  title varchar(50) NOT NULL,
  content mediumtext NOT NULL,
  published datetime NOT NULL,
  updated timestamp NOT NULL DEFAULT current_timestamp on update current_timestamp,
  article_uid int(10) UNSIGNED NOT NULL,
  article_tag_id int(10) UNSIGNED DEFAULT NULL,
  UNIQUE (slug),
  INDEX (published),
  FOREIGN KEY (article_uid) REFERENCES users (uid),
  FOREIGN KEY (article_tag_id) REFERENCES tags (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=2;

CREATE TABLE IF NOT EXISTS meta(
  meta_id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  views int(10) UNSIGNED NOT NULL DEFAULT 0,
  meta_article_id int(10) UNSIGNED NOT NULL,
  INDEX (views),
  FOREIGN KEY (meta_article_id) REFERENCES articles (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=2;
```

