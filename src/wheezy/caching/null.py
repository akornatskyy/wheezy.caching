
""" ``interface`` module.
"""


class NullCache(object):
    """ NullCache is a cache implementation that actually doesn't
        do anything but silently performs cache operations that
        result no change to state.
    """

    def __init__(self):
        pass

    def __enter__(self):  # pragma: nocover
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # pragma: nocover
        pass

    def set(self, key, value, time=0, namespace=None):
        """ Sets a key's value, regardless of previous contents
            in cache.

            >>> c = NullCache()
            >>> c.set('k', 'v')
            True
        """
        return True

    def set_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Set multiple keys' values at once.

            >>> c = NullCache()
            >>> c.set_multi({})
            []
        """
        return []

    def add(self, key, value, time=0, namespace=None):
        """ Sets a key's value, if and only if the item is not
            already.

            >>> c = NullCache()
            >>> c.add('k', 'v')
            True
        """
        return True

    def add_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Adds multiple values at once, with no effect for keys
            already in cache.

            >>> c = NullCache()
            >>> c.add_multi({})
            []
        """
        return []

    def replace(self, key, value, time=0, namespace=None):
        """ Replaces a key's value, failing if item isn't already.

            >>> c = NullCache()
            >>> c.replace('k', 'v')
            True
        """
        return True

    def replace_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Replaces multiple values at once, with no effect for
            keys not in cache.

            >>> c = NullCache()
            >>> c.replace_multi({})
            []
        """
        return []

    def get(self, key, namespace=None):
        """ Looks up a single key.

            >>> c = NullCache()
            >>> c.get('k')
        """
        return None

    def get_multi(self, keys, key_prefix='', namespace=None):
        """ Looks up multiple keys from cache in one operation.
            This is the recommended way to do bulk loads.

            >>> c = NullCache()
            >>> c.get_multi([])
            {}
        """
        return {}

    def delete(self, key, seconds=0, namespace=None):
        """ Deletes a key from cache.

            >>> c = NullCache()
            >>> c.delete('k')
            True
        """
        return True

    def delete_multi(self, keys, seconds=0, key_prefix='', namespace=None):
        """ Delete multiple keys at once.

            >>> c = NullCache()
            >>> c.delete_multi([])
            True
        """
        return True

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically increments a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then incremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.

            >>> c = NullCache()
            >>> c.incr('k')
        """
        return None

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically decrements a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then decremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.

            >>> c = NullCache()
            >>> c.decr('k')
        """
        return None

    def flush_all(self):
        """ Deletes everything in cache.

            >>> c = NullCache()
            >>> c.flush_all()
            True
        """
        return True
