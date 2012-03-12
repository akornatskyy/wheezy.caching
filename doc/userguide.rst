
User Guide
==========

:ref:`wheezy.caching` comes with the following cache implementations:

* CacheClient
* MemoryCache
* NullCache

:ref:`wheezy.caching` provides integration with:

* `python-memcached`_ - Pure Python `memcached`_ client.
* `pylibmc`_ - Quick and small `memcached`_ client for Python written in C.

It introduces idea of *cache dependency* that let effectively invalidate
dependent cache items.

Contract
--------

All cache implementations and integrations provide the same contract. That
means caches can be swapped without a need to modify the code. However
there do exist challenge: some caches are singletons and correctly
provide inter-thread synchronization (thread safe), while others require
an instance per thread (not thread safe), some sort of pooling is
required. In order to provide an easy interchangeable approach for various cache
implementations it is recommended use: factory method plus context
manager.

Let demonstrate this by examples::

    from wheezy.caching.memory import MemoryCache

    # Singleton
    cache = MemoryCache()
    # Factory
    cache_factory = lambda: memory
    # Client code
    with cache_factory() as cache:
        cache.set(...)

Above factory and context manager use is somewhat dummy since you are
fine to work directly with cache. However what happens if at some point
of time you will need to use some other cache implementation (e.g.
pylibmc - `memcached`_ client written in C). The client code will not
change, we just provide another ``cache_factory``::

    from wheezy.caching.pools import EagerPool
    from wheezy.caching.pools import Pooled
    from wheezy.caching.pylibmc import client_factory

    # Cache Pool
    pool = EagerPool(lambda: client_factory(['/tmp/memcached.sock']), size=10)
    # Factory
    cache_factory = lambda: Pooled(pool)
    # Client code
    with cache_factory() as cache:
        cache.set(...)

The client code remains unchanged, however we where able to switch to
completely different cache implementation that requires pooling.

CacheClient
-----------

:py:class:`~wheezy.caching.client.CacheClient` serves mediator purpose
between a single entry point that implements Cache and one or many
namespaces targeted to cache factories.

:py:class:`~wheezy.caching.client.CacheClient` let partition application
cache by namespaces effectively hiding details from client code.

:py:class:`~wheezy.caching.client.CacheClient` accepts the following
arguments:

* ``namespaces`` - a mapping between namespace and cache factory.
* ``default_namespace`` - namespace to use in case it is not specified
  in cache operation.

In the example below we partition application cache into three (default,
membership and funds)::

    from wheezy.caching import ClientCache
    from wheezy.caching import MemoryCache
    from wheezy.caching import NullCache

    default_cache = MemoryCache()
    membership_cache = MemoryCache()
    funds_cache = NullCache()
    cache_factory = lambda: ClientCache({
        'default': lambda: default_cache,
        'membership': lambda: membership_cache,
        'funds': lambda: funds_cache,
    }, default_namespace='default')

Application code is designed to work with a single cache by specifying
namespace to use::

    with cache_factory() as cache:
        cache.add('x1', 1, namespace='default')

At some point of time we might change our partitioning scheme so all
namespaces reside in a single cache::

    default_cache = MemoryCache()
    cache_factory = lambda: ClientCache({
        'default': lambda: default_cache,
        'membership': lambda: default_cache,
        'funds': lambda: default_cache
    }, default_namespace='default')

That happened with no changes to application code, just configuration
settings.

MemoryCache
-----------

:py:class:`~wheezy.caching.memory.MemoryCache` is effective, high
performance in-memory cache implementation. There is no background
routine to invalidate expired items in the cache, instead they are
checked on each get operation.

In order to effectively manage invalidation of expired items (those
that are not actively requested) each item being added to cache is
assigned to time bucket. Each time bucket has a number associated
with a point in time. So if incoming store operation relates to time
bucket N, all items from that bucket are being checked and expired
items removed.

You control a number of buckets during initialization of
:py:class:`~wheezy.caching.memory.MemoryCache`. Here are attributes
that are accepted:

* ``buckets`` - a number of buckets present in cache (defaults to 60).
* ``bucket_interval`` - what is interval in seconds between time buckets
  (defaults to 15).

Interval set by ``bucket_interval`` shows how often items in cache will
be checked for expiration. So if it set to 15 means that every 15 seconds
cache will choose a bucket related to that point in time and all items in
bucket will be checked for expiration. Since there are 60 buckets in the
cache that means only 1/60 part of cache items are locked. This lock
does not impact items requested by ``get``/``get_multi`` operations.
Taking into account this lock happens only once per 15 seconds it cause
minor impact on overall cache performance.

NullCache
---------

:py:class:`~wheezy.caching.null.NullCache` is a cache implementation that
actually does not do anything but silently performs cache operations that
result no change to state.

* ``get``, ``get_multi`` operations always report miss.
* ``set``, ``add``, etc (all store operations) always succeed.

python-memcached
----------------

`python-memcached`_ is a pure Python `memcached`_ client. You can install
this package via easy_install::

    $ env/bin/easy_install python-memcached

Here is a typical use case::

    from wheezy.caching.memcache import client_factory

    cache = client_factory(['unix:/tmp/memcached.sock'])
    cache_factory = lambda: cache

All arguments passed to
:py:meth:`~wheezy.caching.memcache.client_factory` are the same as to
original ``Client`` from python-memcache. Note, `python-memcached`_
``Client`` implementation is *thread local* object.

pylibmc
-------

`pylibmc`_ is a quick and small `memcached`_ client for Python written in C.
Since this package is an interface to *libmemcached* you need development
version of this library so it can be compiled. If you are using Debian::

    apt-get install libmemcached-dev

Now, you can install this package via easy_install::

    $ env/bin/easy_install pylibmc

Here is a typical use case::

    from wheezy.caching.pools import EagerPool
    from wheezy.caching.pools import Pooled
    from wheezy.caching.pylibmc import client_factory

    pool = EagerPool(lambda: client_factory(['/tmp/memcached.sock']), size=10)
    cache_factory = lambda: Pooled(pool)

All arguments passed to
:py:meth:`~wheezy.caching.pylibmc.client_factory` are the same as to
original ``Client`` from pylibmc. Default client factory configures
`pylibmc`_ Client to use binary protocol, tcp_nodelay and ketama
algorithm.

Since `pylibmc`_ implementation is not thread safe it requires pooling,
so we do here. :py:class:`~wheezy.caching.pools.EagerPool` holds
a number of `pylibmc`_ instances, while
:py:class:`~wheezy.caching.pools.Pooled` serves context manager purpose,
effectively acquiring and returning item to the pool.

CacheDependency
---------------

:py:class:`~wheezy.caching.dependency.CacheDependency` introduces a `wire`
between cache items so they can be invalidated via a single operation, thus
simplifying code necessary to manage dependencies in cache.

:py:class:`~wheezy.caching.dependency.CacheDependency` is not related to
any particular cache implementation.

:py:class:`~wheezy.caching.dependency.CacheDependency` can be used to
invalidate items across different cache partitions (namespaces). Note
that ``delete`` must be performed for each namespace and/or cache.

Example
~~~~~~~

Let demostrate this by example. We establish dependency between keys
``k1``, ``k2`` and ``k3``. Please note that dependency does not need to
be passed between various parts of application. You can create it in
one place, than in other, etc. ``CacheDependency`` stores it state in
cache::

    # this is sample from module a.
    dependency = CacheDependency(cache, 'master-key')
    dependency.add_multi(['k1', 'k2', 'k3'])

    # this is sample from module b.
    dependency = CacheDependency(cache, 'master-key')
    dependency.add('k4')

Note that module `b` have no idea about keys used in module `a`. Instead
they share `virtually` cache dependency.

Once we need invalidate items related to cache dependency this is what we
do::

    dependency = CacheDependency(cache, 'master-key')
    dependency.delete()

``delete`` operation must be repeated for each namespace (it doesn't manage
namespace dependency) and/or cache::

    # Using namespaces
    dependency = CacheDependency(cache, 'master-key')
    dependency.delete(namespace='membership')
    dependency.delete(namespace='funds')

    # Using caches
    dependency = CacheDependency(membership_cache, 'master-key')
    dependency.delete()
    dependency = CacheDependency(funds_cache, 'master-key')
    dependency.delete()

Cache dependency is an effective way to reduce coupling between modules
in terms of cache items invalidation.

.. _`memcached`: http://memcached.org
.. _`pylibmc`: http://pypi.python.org/pypi/pylibmc
.. _`python-memcached`: http://pypi.python.org/pypi/python-memcached

