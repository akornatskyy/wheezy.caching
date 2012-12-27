`wheezy.caching`_ is a `python`_ package written in pure Python
code. It is a lightweight caching library that provides integration with:

* `python-memcached`_ - Pure Python `memcached`_ client.
* `pylibmc`_ - Quick and small `memcached`_ client for Python written
  in C.

It introduces idea of *cache dependency* (effectively invalidate dependent
cache items) and other cache related algorithms.

It is optimized for performance, well tested and documented.

Resources:

* `source code`_, `examples`_ and `issues`_ tracker are available
  on `bitbucket`_
* `documentation`_, `readthedocs`_
* `eggs`_ on `pypi`_

Install
-------

`wheezy.caching`_ requires `python`_ version 2.4 to 2.7 or 3.2+.
It is independent of operating system. You can install it from `pypi`_
site using `setuptools`_::

    $ easy_install wheezy.caching

If you are using `virtualenv`_::

    $ virtualenv env
    $ env/bin/easy_install wheezy.caching

If you run into any issue or have comments, go ahead and add on
`bitbucket`_.

.. _`bitbucket`: http://bitbucket.org/akorn/wheezy.caching
.. _`doctest`: http://docs.python.org/library/doctest.html
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
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`source code`: http://bitbucket.org/akorn/wheezy.caching/src
.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
.. _`wheezy.caching`: http://pypi.python.org/pypi/wheezy.caching
