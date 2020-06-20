
User Guide
==========

:ref:`wheezy.caching` comes with the following cache implementations:

* CacheClient
* MemoryCache
* NullCache

:ref:`wheezy.caching` provides integration with:

* `python-memcached`_ - Pure Python `memcached`_ client.
* `pylibmc`_ - Quick and small `memcached`_ client for Python written in C.

It introduces the idea of *cache dependency* that lets you effectively invalidate
dependent cache items.

Contract
--------

All cache implementations and integrations provide the same contract. That
means caches can be swapped without a need to modify the code. However
there does exist a challenge: some caches are singletons and correctly
provide inter-thread synchronization (thread safe), while others require
an instance per thread (not thread safe), for which some sort of pooling is
required. This challenge is transparently resolved.

Here is an example how to configure pylibmc - `memcached`_ (client written
in C): ::

    from wheezy.core.pooling import EagerPool
    from wheezy.caching.pylibmc import MemcachedClient
    from wheezy.caching.pylibmc import client_factory

    # Cache Pool
    pool = EagerPool(lambda: client_factory(['/tmp/memcached.sock']), size=10)
    # Factory
    cache = MemcachedClient(pool)

    # Client code
    cache.set(...)

The client code remains unchanged even some cache implementations
require pooling to remain thread safe.

CacheClient
-----------

:py:class:`~wheezy.caching.client.CacheClient` serves as mediator
between a single entry point that implements Cache and one or many
namespaces targeted to cache factories.

:py:class:`~wheezy.caching.client.CacheClient` lets us partition application
cache by namespaces, effectively hiding details from client code.

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
    cache = ClientCache({
        'default': default_cache,
        'membership': membership_cache,
        'funds': funds_cache,
    }, default_namespace='default')

Application code is designed to work with a single cache by specifying
namespace to use::

    cache.add('x1', 1, namespace='default')

At some point of time we might change our partitioning scheme so all
namespaces reside in a single cache::

    default_cache = MemoryCache()
    cachey = ClientCache({
        'default': default_cache,
        'membership': default_cache,
        'funds': default_cache
    }, default_namespace='default')

What happened with no changes to application code? These are just configuration
settings.

MemoryCache
-----------

:py:class:`~wheezy.caching.memory.MemoryCache` is an effective, high
performance in-memory cache implementation. There is no background
routine to invalidate expired items in the cache, instead they are
checked on each get operation.

In order to effectively manage invalidation of expired items (those
that are not actively requested) each item being added to cache is
assigned to a time bucket. Each time bucket has a number associated
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
result in no change to state.

* ``get``, ``get_multi`` operations always report miss.
* ``set``, ``add``, etc (all store operations) always succeed.

python-memcached
----------------

`python-memcached`_ is a pure Python `memcached`_ client. You can install
this package via pip::

    $ pip install python-memcached

Here is a typical use case::

    from wheezy.caching.memcache import MemcachedClient

    cache = MemcachedClient(['unix:/tmp/memcached.sock'])

You can specify a key encoding function by passing a ``key_encode`` argument that
must be a callable that does key encoding. By default
:py:meth:`~wheezy.caching.encoding.string_encode` is applied.

All arguments passed to
:py:meth:`~wheezy.caching.memcache.MemcachedClient` are the same as those passed to
the original ``Client`` from python-memcache. Note, `python-memcached`_
``Client`` implementation is *thread local* object.

pylibmc
-------

`pylibmc`_ is a quick and small `memcached`_ client for Python written in C.
Since this package is an interface to *libmemcached*, you need the development
version of this library installed so pylibmc can be compiled. If you are using Debian::

    apt-get install libmemcached-dev

Now, you can install this package via pip::

    $ pip install pylibmc

Here is a typical use case::

    from wheezy.core.pooling import EagerPool
    from wheezy.caching.pylibmc import MemcachedClient
    from wheezy.caching.pylibmc import client_factory

    pool = EagerPool(lambda: client_factory(['/tmp/memcached.sock']), size=10)
    cache = MemcachedClient(pool)

You can specify a key encoding function by passing a ``key_encode`` argument that
must be a callable that does key encoding. By default
:py:meth:`~wheezy.caching.encoding.string_encode` is applied.

All arguments passed to
:py:meth:`~wheezy.caching.pylibmc.client_factory` are the same as those passed to
the original ``Client`` from pylibmc. Default client factory configures
`pylibmc`_ Client to use binary protocol, tcp_nodelay and ketama
algorithm.

Since `pylibmc`_ implementation is not thread safe it requires pooling,
as we do here. :py:class:`~wheezy.core.pooling.EagerPool` holds
a number of `pylibmc`_ instances.

Key Encoding
------------

`Memcached`_ has some restrictions concerning the keys used. Text protocol requires
a valid key that contains only ASCII characters except space (0x20), carriage
return (0x0d), and line feed (0x0a), since these characters are meaningful in
text protocol. Key length is restricted to 250.

* :py:meth:`~wheezy.caching.encoding.string_encode` - encodes ``key`` with
  UTF-8 encoding.
* :py:meth:`~wheezy.caching.encoding.base64_encode` - encodes ``key`` with
  base64 encoding.
* :py:meth:`~wheezy.caching.encoding.hash_encode` - encodes ``key`` with
  given hash function. See list of available hashes in ``hashlib`` module
  from the Python Statndard Library. Additional algorithms may also be available
  depending upon the OpenSSL library that Python uses on your platform.

There is a general purpose function:

* :py:meth:`~wheezy.caching.encoding.encode_keys` - encodes all keys in mapping
  with ``key_encode`` callable. Returns a tuple of: *key mapping*
  (encoded key => key) and *value mapping* (encoded key => value).

You can specify the key encoding function to use, by passing the ``key_encode``
argument to *memcache* and/or *pylibmc* cache factory.

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

Master Key
~~~~~~~~~~

It is important to avoid key collisions for the master key due to the way
in which dependency keys are built. The dependency keys are built by
adding a suffix with incremental number to the master key, e.g. if master
key is 'key' than dependent keys used by CacheDependency will be 'key1',
'key2', 'key3', etc. The master key stores the number of dependent keys
thus this number is incremented each time you add something to
a dependency.

If a master key is composed as a concatenation with some id it
must be suffixed with a delimiter (a symbol that is not part of the
id) to avoid key collision. In the example below id is a number
so choosing ':' as a delimiter suites our needs::

    def master_key_order(id):
        return 'mk:order:' + str(id) + ':'

For order id 100 the master key is 'mk:order:100:' and
dependent keys take space 'mk:order:100:1' for the first item added,
'mk:order:100:2' for the second, etc. If we add 2 items to cache
dependency the value stored by the master key is 2.

Example
~~~~~~~

Let's demostrate this by example. We establish dependency between keys
``k1``, ``k2`` and ``k3`` for 600 seconds. Please note that dependency
does not need to be passed between various parts of application. You
can create it in one place, than in other, etc. ``CacheDependency``
stores it state in cache::

    # this is sample from module a.
    dependency = CacheDependency('master-key', time=600)
    dependency.add_multi(cache, ['k1', 'k2', 'k3'])

    # this is sample from module b.
    dependency = CacheDependency('master-key', time=600)
    dependency.add(cache, 'k4')

Note that module `b` has no idea about keys used in module `a`. Instead
they share a cache dependency `virtually`.

Once we need to invalidate items related to cache dependencies, this is what we
do::

    dependency = CacheDependency('master-key')
    dependency.delete(cache)

``delete`` operation must be repeated for each namespace (it doesn't manage
namespace dependency) and/or cache::

    # Using namespaces
    dependency = CacheDependency('master-key')
    dependency.delete(cache, namespace='membership')
    dependency.delete(cache, namespace='funds')

    # Using caches
    dependency = CacheDependency('master-key')
    dependency.delete(membership_cache)
    dependency.delete(funds_cache)

Cache dependency is an effective way to reduce coupling between modules
in terms of cache item invalidation.

.. _`memcached`: http://memcached.org
.. _`pylibmc`: http://pypi.python.org/pypi/pylibmc
.. _`python-memcached`: http://pypi.python.org/pypi/python-memcached

