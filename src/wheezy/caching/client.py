
""" ``client`` module.
"""


class CacheClient(object):
    """ CacheClient serves mediator purpose between a single entry
        point that implements Cache and one or many namespaces
        targeted to concrete cache factories.

        CacheClient let partition application cache by namespaces
        effectively hiding details from client code.
    """

    def __init__(self, namespaces, default_namespace):
        """
            ``namespaces`` - a mapping between namespace and cache factory.
            ``default_namespace`` - namespace to use in case it is not
                specified in cache operation.
        """
        self.default_namespace = default_namespace
        self.default = namespaces.pop(default_namespace)
        self.namespaces = namespaces

    def __enter__(self):  # pragma: nocover
        self.context = context = self.default()
        self.default_cache = context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # pragma: nocover
        self.context.__exit__(exc_type, exc_value, traceback)
        self.context = None

    def set(self, key, value, time=0, namespace=None):
        """ Sets a key's value, regardless of previous contents
            in cache.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.set(key, value, time, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.set(key, value, time, namespace)
            finally:
                context.__exit__(None, None, None)

    def set_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Set multiple keys' values at once.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.set_multi(
                mapping, time, key_prefix, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.set_multi(mapping, time, key_prefix, namespace)
            finally:
                context.__exit__(None, None, None)

    def add(self, key, value, time=0, namespace=None):
        """ Sets a key's value, if and only if the item is not
            already.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.add(key, value, time, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.add(
                    key, value, time, namespace)
            finally:
                context.__exit__(None, None, None)

    def add_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Adds multiple values at once, with no effect for keys
            already in cache.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.add_multi(
                mapping, time, key_prefix, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.add_multi(
                    mapping, time, key_prefix, namespace)
            finally:
                context.__exit__(None, None, None)

    def replace(self, key, value, time=0, namespace=None):
        """ Replaces a key's value, failing if item isn't already.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.replace(key, value, time, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.replace(key, value, time, namespace)
            finally:
                context.__exit__(None, None, None)

    def replace_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Replaces multiple values at once, with no effect for
            keys not in cache.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.replace_multi(
                mapping, time, key_prefix, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.replace_multi(
                    mapping, time, key_prefix, namespace)
            finally:
                context.__exit__(None, None, None)

    def get(self, key, namespace=None):
        """ Looks up a single key.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.get(key, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.get(key, namespace)
            finally:
                context.__exit__(None, None, None)

    def get_multi(self, keys, key_prefix='', namespace=None):
        """ Looks up multiple keys from cache in one operation.
            This is the recommended way to do bulk loads.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.get_multi(keys, key_prefix, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.get_multi(keys, key_prefix, namespace)
            finally:
                context.__exit__(None, None, None)

    def delete(self, key, seconds=0, namespace=None):
        """ Deletes a key from cache.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.delete(key, seconds, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.delete(key, seconds, namespace)
            finally:
                context.__exit__(None, None, None)

    def delete_multi(self, keys, seconds=0, key_prefix='', namespace=None):
        """ Delete multiple keys at once.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.delete_multi(
                keys, seconds, key_prefix, namespace)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.delete_multi(
                    keys, seconds, key_prefix, namespace)
            finally:
                context.__exit__(None, None, None)

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically increments a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then incremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.incr(
                key, delta, namespace, initial_value)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.incr(key, delta, namespace, initial_value)
            finally:
                context.__exit__(None, None, None)

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically decrements a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then decremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.
        """
        if namespace is None or namespace == self.default_namespace:
            return self.default_cache.decr(
                key, delta, namespace, initial_value)
        else:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                return cache.decr(key, delta, namespace, initial_value)
            finally:
                context.__exit__(None, None, None)

    def flush_all(self):
        """ Deletes everything in cache.
        """
        succeed = self.default_cache.flush_all()
        for namespace in self.namespaces:
            context = self.namespaces[namespace]()
            cache = context.__enter__()
            try:
                succeed &= cache.flush_all()
            finally:
                context.__exit__(None, None, None)
        return succeed
