.. _`wheezy.caching`:

wheezy.caching
==============

Introduction
------------

:ref:`wheezy.caching` is a `python`_ package written in pure Python code.
It is a lightweight caching library that provides integration with:

* `python-memcached`_ - Pure Python `memcached`_ client.
* `pylibmc`_ - Quick and small `memcached`_ client for Python written in C.

It introduces the idea of *cache dependency* (effectively invalidate dependent
cache items) and other cache related algorithms.

It is optimized for performance, well tested and documented.

Resources:

* `source code`_ and `issues`_ tracker are available
  on `github`_
* `documentation`_

Contents
--------

.. toctree::
   :maxdepth: 2

   gettingstarted
   examples
   userguide
   modules

.. _`github`: https://github.com/akornatskyy/wheezy.caching
.. _`documentation`: https://wheezycaching.readthedocs.io/en/latest/
.. _`issues`: https://github.com/akornatskyy/wheezy.caching/issues
.. _`memcached`: http://memcached.org
.. _`pylibmc`: http://pypi.python.org/pypi/pylibmc
.. _`python`: http://www.python.org
.. _`python-memcached`: http://pypi.python.org/pypi/python-memcached
.. _`source code`: https://github.com/akornatskyy/wheezy.caching
