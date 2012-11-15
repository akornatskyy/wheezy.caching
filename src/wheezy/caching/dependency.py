
""" ``dependency`` module.
"""

from wheezy.caching.comp import itervalues
from wheezy.caching.comp import xrange


class CacheDependency(object):
    """ CacheDependency introduces a `wire` between cache items
        so they can be invalidated via a single operation, thus
        simplifing code necessary to manage dependencies in cache.
    """

    __slots__ = ('cache', 'master_key', 'time', 'namespace')

    def __init__(self, cache, master_key, time=0, namespace=None):
        """
           *cache* - a cache instance to be used to track dependencies.
           *master_key* - a key used to track a number of issued dependencies.
           *time* - a time in seconds to keep dependent keys.
           *namespace* - a default namespace.
        """
        self.cache = cache
        self.master_key = master_key
        self.time = time
        self.namespace = namespace

    def next_key(self, namespace=None):
        """ Returns the next unique key for dependency.
        """
        return self.master_key + str(self.cache.incr(
            self.master_key, 1, namespace or self.namespace, 0))

    def next_keys(self, n, namespace=None):
        """ Returns ``n`` number of dependency keys.
        """
        last_id = self.cache.incr(self.master_key, n,
                                  namespace or self.namespace, 0)
        return [self.master_key + str(i)
                for i in xrange(last_id - n + 1, last_id + 1)]

    def add(self, key, namespace=None):
        """ Adds a given key to dependency.
        """
        namespace = namespace or self.namespace
        return self.cache.add(self.next_key(namespace),
                              key, self.time, namespace)

    def add_multi(self, keys, key_prefix='', namespace=None):
        """ Adds several keys to dependency.
        """
        namespace = namespace or self.namespace
        mapping = dict(zip(self.next_keys(
            len(keys), namespace),
            key_prefix and map(lambda k: key_prefix + k, keys) or keys))
        return self.cache.add_multi(mapping, self.time, '', namespace)

    def delete(self, namespace=None):
        """ Delete all items wired by this cache dependency.
        """
        namespace = namespace or self.namespace
        cache = self.cache
        n = cache.get(self.master_key, namespace)
        if n is None:
            return True
        keys = [self.master_key + str(i) for i in xrange(1, n + 1)]
        keys.extend(itervalues(cache.get_multi(keys, '', namespace)))
        keys.append(self.master_key)
        return cache.delete_multi(keys, 0, '', namespace)
