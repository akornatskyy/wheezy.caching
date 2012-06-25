
""" ``dependency`` module.
"""

from wheezy.caching.comp import itervalues
from wheezy.caching.comp import xrange


class CacheDependency(object):
    """ CacheDependency introduces a `wire` between cache items
        so they can be invalidated via a single operation, thus
        simplifing code necessary to manage dependencies in cache.
    """

    __slots__ = ['master_key', 'time']

    def __init__(self, master_key, time=0):
        self.master_key = master_key
        self.time = time

    def next_key(self, cache, namespace=None):
        """ Returns the next unique key for dependency.

            >>> from wheezy.caching.memory import MemoryCache
            >>> d = CacheDependency('key')
            >>> c = MemoryCache()
            >>> d.next_key(c)
            'key1'
            >>> d.next_key(c)
            'key2'
        """
        return self.master_key + str(cache.incr(
            self.master_key, 1, namespace, 0))

    def next_keys(self, cache, n, namespace=None):
        """ Returns ``n`` number of dependency keys.

            >>> from wheezy.caching.memory import MemoryCache
            >>> d = CacheDependency('key')
            >>> c = MemoryCache()
            >>> d.next_keys(c, 1)
            ['key1']
            >>> d.next_keys(c, 3)
            ['key2', 'key3', 'key4']
        """
        last_id = cache.incr(self.master_key, n, namespace, 0)
        return [self.master_key + str(i)
                for i in xrange(last_id - n + 1, last_id + 1)]

    def add(self, cache, key, namespace=None):
        """ Adds a given key to dependency.

            >>> from wheezy.caching.memory import MemoryCache
            >>> d = CacheDependency('key')
            >>> c = MemoryCache()
            >>> d.add(c, 'key-x')
            True
            >>> c.get('key1')
            'key-x'
        """
        return cache.add(
            self.next_key(cache, namespace),
            key, self.time, namespace)

    def add_multi(self, cache, keys, key_prefix='', namespace=None):
        """ Adds several keys to dependency.

            >>> from wheezy.caching.memory import MemoryCache
            >>> d = CacheDependency('key')
            >>> c = MemoryCache()
            >>> d.add_multi(c, ('key-x', 'key-y'))
            []
            >>> c.get('key1')
            'key-x'
            >>> c.get('key2')
            'key-y'

            With ``key_prefix``

            >>> d.add_multi(c, ('a', 'b'), key_prefix='key-')
            []
            >>> c.get('key3')
            'key-a'
            >>> c.get('key4')
            'key-b'
        """
        mapping = dict(zip(
            self.next_keys(cache, len(keys), namespace),
            map(lambda k: key_prefix + k, keys)))
        return cache.add_multi(mapping, self.time, '', namespace)

    def delete(self, cache, namespace=None):
        """ Delete all items wired by this cache dependency.

            >>> from wheezy.caching.memory import MemoryCache
            >>> d = CacheDependency('key')
            >>> c = MemoryCache()

            If there are no dependent items, delete succeed.

            >>> d.delete(c)
            True

            Clears all dependent items

            >>> mapping = {'key-x': 1, 'key-y': 2}
            >>> c.set_multi(mapping, 100)
            []
            >>> d.add_multi(c, mapping.keys())
            []
            >>> len(c.items)
            5
            >>> d.delete(c)
            True
            >>> len(c.items)
            0
        """
        n = cache.get(self.master_key, namespace)
        if n is None:
            return True
        keys = [self.master_key + str(i) for i in xrange(1, n + 1)]
        keys.extend(itervalues(
            cache.get_multi(keys, '', namespace)))
        keys.append(self.master_key)
        return cache.delete_multi(keys, 0, '', namespace)
