
""" ``client`` module.
"""


class CacheClient(object):
    """ CacheClient serves mediator purpose between a single entry
        point that implements Cache and one or many namespaces
        targeted to concrete cache implementations. CacheClient
        let partition application cache by namespaces effectively
        hiding details from client code.
    """

    def __init__(self, namespaces, default_namespace):
        """
            ``namespaces`` - a mapping between namespace and cache
            ``default_namespace`` - namespace to use in case it is not
                specified in cache operation.
        """
        self.default = namespaces[default_namespace]
        self.namespaces = namespaces

    def __enter__(self):  # pragma: nocover
        return self.default.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):  # pragma: nocover
        self.default.__exit__(exc_type, exc_value, traceback)

    def set(self, key, value, time=0, namespace=None):
        """ Sets a key's value, regardless of previous contents
            in cache.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.set('x', 1)
            True

            Namespace is used explicitely.

            >>> c.set('x', 1, namespace='n1')
            True
        """
        if namespace is None:
            return self.default.set(key, value, time, namespace)
        else:
            return self.namespaces[namespace].set(
                    key, value, time, namespace)

    def set_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Set multiple keys' values at once.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.set_multi({})
            []

            Namespace is used explicitely.

            >>> c.set_multi({}, namespace='n1')
            []
        """
        if namespace is None:
            return self.default.set_multi(
                    mapping, time, key_prefix, namespace)
        else:
            return self.namespaces[namespace].set_multi(
                    mapping, time, key_prefix, namespace)

    def add(self, key, value, time=0, namespace=None):
        """ Sets a key's value, if and only if the item is not
            already.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.add('x', 1)
            True

            Namespace is used explicitely.

            >>> c.add('x', 1, namespace='n1')
            True
        """
        if namespace is None:
            return self.default.add(key, value, time, namespace)
        else:
            return self.namespaces[namespace].add(
                    key, value, time, namespace)

    def add_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Adds multiple values at once, with no effect for keys
            already in cache.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.add_multi({})
            []

            Namespace is used explicitely.

            >>> c.add_multi({}, namespace='n1')
            []
        """
        if namespace is None:
            return self.default.add_multi(
                    mapping, time, key_prefix, namespace)
        else:
            return self.namespaces[namespace].add_multi(
                    mapping, time, key_prefix, namespace)

    def replace(self, key, value, time=0, namespace=None):
        """ Replaces a key's value, failing if item isn't already.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.replace('x', 1)
            True

            Namespace is used explicitely.

            >>> c.replace('x', 1, namespace='n1')
            True
        """
        if namespace is None:
            return self.default.replace(key, value, time, namespace)
        else:
            return self.namespaces[namespace].replace(
                    key, value, time, namespace)

    def replace_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Replaces multiple values at once, with no effect for
            keys not in cache.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.replace_multi({})
            []

            Namespace is used explicitely.

            >>> c.replace_multi({}, namespace='n1')
            []
        """
        if namespace is None:
            return self.default.replace_multi(
                    mapping, time, key_prefix, namespace)
        else:
            return self.namespaces[namespace].replace_multi(
                    mapping, time, key_prefix, namespace)

    def get(self, key, namespace=None):
        """ Looks up a single key.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.get('x')

            Namespace is used explicitely.

            >>> c.get('x', namespace='n1')
        """
        if namespace is None:
            return self.default.get(key, namespace)
        else:
            return self.namespaces[namespace].get(key, namespace)

    def get_multi(self, keys, key_prefix='', namespace=None):
        """ Looks up multiple keys from cache in one operation.
            This is the recommended way to do bulk loads.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.get_multi([])
            {}

            Namespace is used explicitely.

            >>> c.get_multi([], namespace='n1')
            {}
        """
        if namespace is None:
            return self.default.get_multi(keys, key_prefix, namespace)
        else:
            return self.namespaces[namespace].get_multi(
                    keys, key_prefix, namespace)

    def delete(self, key, seconds=0, namespace=None):
        """ Deletes a key from cache.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.delete('x')
            True

            Namespace is used explicitely.

            >>> c.delete('x', namespace='n1')
            True
        """
        if namespace is None:
            return self.default.delete(key, seconds, namespace)
        else:
            return self.namespaces[namespace].delete(key, seconds, namespace)

    def delete_multi(self, keys, seconds=0, key_prefix='', namespace=None):
        """ Delete multiple keys at once.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.delete_multi([])
            True

            Namespace is used explicitely.

            >>> c.delete_multi([], namespace='n1')
            True
        """
        if namespace is None:
            return self.default.delete_multi(
                    keys, seconds, key_prefix, namespace)
        else:
            return self.namespaces[namespace].delete_multi(
                    keys, seconds, key_prefix, namespace)

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically increments a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then incremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.incr('x')

            Namespace is used explicitely.

            >>> c.incr('x', namespace='n1')
        """
        if namespace is None:
            return self.default.incr(key, delta, namespace, initial_value)
        else:
            return self.namespaces[namespace].incr(
                    key, delta, namespace, initial_value)

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically decrements a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then decremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            Using default namespace.

            >>> c.decr('x')

            Namespace is used explicitely.

            >>> c.decr('x', namespace='n1')
        """
        if namespace is None:
            return self.default.decr(key, delta, namespace, initial_value)
        else:
            return self.namespaces[namespace].decr(
                    key, delta, namespace, initial_value)

    def flush_all(self):
        """ Deletes everything in cache.

            >>> from wheezy.caching.null import NullCache
            >>> c = CacheClient(namespaces={
            ...         'n1': NullCache()
            ... }, default_namespace='n1')

            >>> c.flush_all()
            True
        """
        succeed = True
        for client in self.namespaces.values():
            succeed &= client.flush_all()
        return succeed
