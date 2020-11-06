""" ``dependency`` module.
"""

from wheezy.caching.utils import total_seconds


class CacheDependency(object):
    """CacheDependency introduces a `wire` between cache items
    so they can be invalidated via a single operation, thus
    simplifing code necessary to manage dependencies in cache.
    """

    def __init__(self, cache, time=0, namespace=None):
        """
        *cache* - a cache instance to be used to track dependencies.
        *time* - a time in seconds to keep dependent keys.
        *namespace* - a default namespace.
        """
        self.cache = cache
        self.time = total_seconds(time)
        self.namespace = namespace

    def next_key(self, master_key):
        """Returns the next unique key for dependency.

        *master_key* - a key used to track a number of issued dependencies.
        """
        return master_key + str(
            self.cache.incr(master_key, 1, self.namespace, 0)
        )

    def next_keys(self, master_key, n):
        """Returns *n* number of dependency keys.

        *master_key* - a key used to track a number of issued dependencies.
        """
        last_id = self.cache.incr(master_key, n, self.namespace, 0)
        return [
            master_key + str(i) for i in range(last_id - n + 1, last_id + 1)
        ]

    def add(self, master_key, key):
        """Adds a given *key* to dependency."""
        return self.cache.add(
            self.next_key(master_key), key, self.time, self.namespace
        )

    def add_multi(self, master_key, keys):
        """Adds several *keys* to dependency."""
        mapping = dict(zip(self.next_keys(master_key, len(keys)), keys))
        return self.cache.add_multi(mapping, self.time, self.namespace)

    def get_keys(self, master_key):
        """Returns all keys wired by *master_key* cache dependency."""
        n = self.cache.get(master_key, self.namespace)
        if n is None:
            return []
        keys = [master_key + str(i) for i in range(1, n + 1)]
        keys.extend(self.cache.get_multi(keys, self.namespace).values())
        keys.append(master_key)
        return keys

    def get_multi_keys(self, master_keys):
        """Returns all keys wired by *master_keys* cache dependencies."""
        numbers = self.cache.get_multi(master_keys, self.namespace)
        if not numbers:
            return []
        keys = [
            master_key + str(i)
            for master_key, n in numbers.items()
            for i in range(1, n + 1)
        ]
        keys.extend(self.cache.get_multi(keys, self.namespace).values())
        keys.extend(master_keys)
        return keys

    def delete(self, master_key):
        """Delete all items wired by *master_key* cache dependency."""
        keys = self.get_keys(master_key)
        if not keys:
            return True
        return self.cache.delete_multi(keys, 0, self.namespace)

    def delete_multi(self, master_keys):
        """Delete all items wired by *master_keys* cache dependencies."""
        keys = self.get_multi_keys(master_keys)
        if not keys:
            return True
        return self.cache.delete_multi(keys, 0, self.namespace)
