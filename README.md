# wheezy.caching

[![Build Status](https://travis-ci.org/akornatskyy/wheezy.caching.svg?branch=master)](https://travis-ci.org/akornatskyy/wheezy.caching)
[![Coverage Status](https://coveralls.io/repos/github/akornatskyy/wheezy.caching/badge.svg?branch=master)](https://coveralls.io/github/akornatskyy/wheezy.caching?branch=master)
[![Documentation Status](https://readthedocs.org/projects/wheezycaching/badge/?version=latest)](https://wheezycaching.readthedocs.io/en/latest/?badge=latest)
[![pypi version](https://badge.fury.io/py/wheezy.caching.svg)](https://badge.fury.io/py/wheezy.caching)

[wheezy.caching](https://pypi.org/project/wheezy.caching/) is a
[python](http://www.python.org) package written in pure Python code. It
is a lightweight caching library that provides integration with:

- [python-memcached](https://pypi.org/project/python-memcached/) -
  Pure Python [memcached](http://memcached.org) client.
- [pylibmc](https://pypi.org/project/pylibmc/) - Quick and small
  [memcached](http://memcached.org) client for Python written in C.

It introduces idea of *cache dependency* (effectively invalidate
dependent cache items) and other cache related algorithms.

It is optimized for performance, well tested and documented.

Resources:

- [source code](https://github.com/akornatskyy/wheezy.caching)
  and [issues](https://github.com/akornatskyy/wheezy.caching/issues)
  tracker are available on
  [github](https://github.com/akornatskyy/wheezy.caching)
- [documentation](https://wheezycaching.readthedocs.io/en/latest/)

## Install

[wheezy.caching](https://pypi.org/project/wheezy.caching/) requires
[python](http://www.python.org) version 3.8+. It is independent of operating
system. You can install it from
[pypi](https://pypi.org/project/wheezy.caching/) site:

```sh
pip install -U wheezy.caching
pip install -U wheezy.caching[pylibmc]
pip install -U wheezy.caching[python-memcached]
```

If you run into any issue or have comments, go ahead and add on
[github](https://github.com/akornatskyy/wheezy.caching).
