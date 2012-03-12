
Examples
========

We start with a simple example. Before we proceed
let setup `virtualenv`_ environment::

    $ virtualenv env
    $ env/bin/easy_install wheezy.caching

.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv

Playing Around
--------------

We are going create a number of items, add them to cache, try get them
back, establish dependency and finally invalidate all together::

    from wheezy.caching import MemoryCache as Cache
    from wheezy.caching import CacheDependency

    cache = Cache()

    # Add a single item
    cache.add('k1', 1)

    # Add few more
    cache.add_multi({'k2': 2, 'k3': 3})

    # Get a single item
    cache.get('k2')

    # Get several at once
    cache.get_multi(['k1', 'k2', 'k3'])

    # Establish dependency somewhere in code place A
    dependency = CacheDependency('master-key')
    dependency.add(cache, 'k1')

    # Establish dependency somewhere in code place B
    dependency.add_multi(cache, ['k1', 'k2', 'k3'])

    # Invalidate dependency somewhere in code place C
    dependency.delete(cache)
