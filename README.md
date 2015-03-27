###Demo仅供学习测试



##介绍

>简单博客程序.

>参考了tornado中的实例.


##依赖

* python2.7
* tornado
* torndb
* MySQL
* MySQL-python
* markdown


##使用的js库

* SyntaxHighlighter 3.0.83
* jQuery v2.1.1
* jquery.scrollTo-1.1.13
* jsSHA/1.6.0/sha1.js

##MySQL表结构

<pre><code>
CREATE TABLE IF NOT EXISTS `entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author_id` int(11) NOT NULL,
  `slug` varchar(20) NOT NULL,
  `title` varchar(100) NOT NULL,
  `markdown` mediumtext NOT NULL,
  `html` mediumtext NOT NULL,
  `published` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `published` (`published`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;
</pre></code>

<pre><code>
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;
</pre></code>

