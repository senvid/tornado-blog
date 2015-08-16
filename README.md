##Demo仅供学习


###介绍

简单博客程序.

参考了tornado中的实例.


###依赖

* python2.7
* tornado
* torndb
* MySQL
* MySQL-python
* markdown


###使用的js库

- [x] SyntaxHighlighter 3.0.83
- [x] jQuery v2.1.1
- [x] jquery.scrollTo-1.1.13
- [x] jsSHA/1.6.0/sha1.js

###MySQL表结构

```
CREATE TABLE IF NOT EXISTS `entries` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `author_id` int(11) NOT NULL,
  `slug` varchar(50) NOT NULL UNIQUE,
  `title` varchar(100) NOT NULL,
  `markdown` mediumtext NOT NULL,
  `html` mediumtext NOT NULL,
  `published` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `published` (`published`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;
```

```
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `email` varchar(50) NOT NULL UNIQUE,
  `password` varchar(50) NOT NULL,
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;
```

