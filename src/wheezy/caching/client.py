""" ``client`` module.
"""


class CacheClient(object):
    """CacheClient serves mediator purpose between a single entry
    point that implements Cache and one or many namespaces
    targeted to concrete cache implementations.

    CacheClient let partition application cache by namespaces
    effectively hiding details from client code.
    """

    def __init__(self, namespaces, default_namespace):
        """
        ``namespaces`` - a mapping between namespace and cache.
        ``default_namespace`` - namespace to use in case it is not
            specified in cache operation.
        """
        self.default_namespace = default_namespace
        self.namespaces = namespaces

    def set(self, key, value, time=0, namespace=None):
        """Sets a key's value, regardless of previous contents
        in cache.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].set(key, value, time, namespace)

    def set_multi(self, mapping, time=0, namespace=None):
        """Set multiple keys' values at once."""
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].set_multi(mapping, time, namespace)

    def add(self, key, value, time=0, namespace=None):
        """Sets a key's value, if and only if the item is not
        already.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].add(key, value, time, namespace)

    def add_multi(self, mapping, time=0, namespace=None):
        """Adds multiple values at once, with no effect for keys
        already in cache.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].add_multi(mapping, time, namespace)

    def replace(self, key, value, time=0, namespace=None):
        """Replaces a key's value, failing if item isn't already."""
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].replace(key, value, time, namespace)

    def replace_multi(self, mapping, time=0, namespace=None):
        """Replaces multiple values at once, with no effect for
        keys not in cache.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].replace_multi(
            mapping, time, namespace
        )

    def get(self, key, namespace=None):
        """Looks up a single key."""
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].get(key, namespace)

    def get_multi(self, keys, namespace=None):
        """Looks up multiple keys from cache in one operation.
        This is the recommended way to do bulk loads.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].get_multi(keys, namespace)

    def delete(self, key, seconds=0, namespace=None):
        """Deletes a key from cache."""
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].delete(key, seconds, namespace)

    def delete_multi(self, keys, seconds=0, namespace=None):
        """Delete multiple keys at once."""
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].delete_multi(
            keys, seconds, namespace
        )

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        """Atomically increments a key's value. The value, if too
        large, will wrap around.

        If the key does not yet exist in the cache and you specify
        an initial_value, the key's value will be set to this
        initial value and then incremented. If the key does not
        exist and no initial_value is specified, the key's value
        will not be set.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].incr(
            key, delta, namespace, initial_value
        )

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        """Atomically decrements a key's value. The value, if too
        large, will wrap around.

        If the key does not yet exist in the cache and you specify
        an initial_value, the key's value will be set to this
        initial value and then decremented. If the key does not
        exist and no initial_value is specified, the key's value
        will not be set.
        """
        namespace = namespace or self.default_namespace
        return self.namespaces[namespace].decr(
            key, delta, namespace, initial_value
        )

    def flush_all(self):
        """Deletes everything in cache."""
        succeed = True
        for cache in self.namespaces.values():
            succeed &= cache.flush_all()
        return succeed
