.. _`wheezy.caching`:

Wheezy Caching
==============

Introduction
------------

:ref:`wheezy.caching` is a `python`_ package written in pure Python code.
It is a lightweight caching library that provides integration with:

* `python-memcached`_ - Pure Python `memcached`_ client.
* `pylibmc`_ - Quick and small `memcached`_ client for Python written in C.

It introduces idea of *cache dependency* that let effectively invalidate
dependent cache items as well as other cache related algorithms.

It is optimized for performance, well tested and documented.

Resources:

* `source code`_, `examples`_ and `issues`_ tracker are available
  on `bitbucket`_
* `documentation`_, `readthedocs`_
* `eggs`_ on `pypi`_

Contents
--------

.. toctree::
   :maxdepth: 2

   gettingstarted
   examples
   userguide
   modules

.. _`bitbucket`: http://bitbucket.org/akorn/wheezy.caching
.. _`documentation`: http://packages.python.org/wheezy.caching
.. _`eggs`: http://pypi.python.org/pypi/wheezy.caching
.. _`examples`: http://bitbucket.org/akorn/wheezy.caching/src/tip/demos
.. _`issues`: http://bitbucket.org/akorn/wheezy.caching/issues
.. _`memcached`: http://memcached.org
.. _`pylibmc`: http://pypi.python.org/pypi/pylibmc
.. _`pypi`: http://pypi.python.org
.. _`python`: http://www.python.org
.. _`python-memcached`: http://pypi.python.org/pypi/python-memcached
.. _`readthedocs`: http://readthedocs.org/builds/wheezycaching
.. _`source code`: http://bitbucket.org/akorn/wheezy.caching/src

