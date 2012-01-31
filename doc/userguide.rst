
User Guide
==========

:ref:`wheezy.caching` comes with the following cache implementations:

* CacheClient
* MemoryCache
* NullCache

It introduces idea of cache dependency that let effectively invalidate
dependent cache items.

CacheClient
-----------

:py:class:`~wheezy.caching.client.CacheClient` serves mediator purpose 
between a single entry point that implements Cache and one or many 
namespaces targeted to concrete cache implementations. 

:py:class:`~wheezy.caching.client.CacheClient` let partition application 
cache by namespaces effectively hiding details from client code.

:py:class:`~wheezy.caching.client.CacheClient` acepts the following
arguments:

* ``namespaces`` - a mapping between namespace and cache
* ``default_namespace`` - namespace to use in case it is not specified
  in cache operation.

In the example below we partition application cache into three (default,
membership and funds)::

    from wheezy.caching import ClientCache
    from wheezy.caching import MemoryCache
    from wheezy.caching import NullCache
    
    cache = ClientCache({
        'default': MemoryCache(),
        'membership': MemoryCache(),
        'funds': NullCache(),
    }, default_namespace='default')
    
Application code is designed to work with a single cache by specifying
namespace to use::

    cache.add('x1', 1, namespace='default')
    
At somepoint of time we might change our partitioning scheme so all 
namespaces reside in a single cache::

    cache = MemoryCache()
    cache = ClientCache({
        'default': cache,
        'membership': cache,
        'funds': cache,
    }, default_namespace='default')

That happend we no changes to application code, just configuration
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
with point of time. So if incoming store in cache operation relates
to time bucket N, all items from what bucket are being checked and
expired items removed.

You control a number of buckets during initialization of 
:py:class:`~wheezy.caching.memory.MemoryCache`. Here are attributes
that are acepted:

* ``buckets`` - a number of buckets present in cache (defaults to 60).
* ``bucket_interval`` - what is interval in seconds between time buckets 
  (defaults to 15).

Inteval set by ``bucket_interval`` shows how often items in cache will
be checked for expiration. So if it set to 15 means that every 15 seconds
cache will choose a bucket related to that point of time and all items in 
bucket will be checked for expiration. Since there are 60 buckets in the
cache that means only 1/60 part of cache items are locked. This lock
does not impact items requested by ``get``/``get_multi`` operations. 
Taking into account this lock happens only once per 15 seconds it cause 
minor impact on overal cache performance.

NullCache
---------

:py:class:`~wheezy.caching.null.NullCache` is a cache implementation that 
actually doesn't do anything but silently performs cache operations that
result no change to state.

* ``get``, ``get_multi`` operations always report miss.
* ``set``, ``add``, etc (all store operations) always succeed.

CacheDependency
---------------

:py:class:`~wheezy.caching.dependency.CacheDependency` introduces a `wire` 
between cache items so they can be invalidated via a single operation, thus
simplifing code necessary to manage dependencies in cache.

:py:class:`~wheezy.caching.dependency.CacheDependency` is not related to
any particular cache implementation.

:py:class:`~wheezy.caching.dependency.CacheDependency` can be used to
invalidate items across different cache partitions (namespaces). Note
that ``delete`` must be performed for each namespace.





















