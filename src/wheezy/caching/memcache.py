
""" ``memcache`` module.
"""

try:
    Client = __import__('memcache', None, None, ['Client']).Client

    def client_factory(*args, **kwargs):
        """ Client factory for python-memcache.
        """
        return MemcachedClient(Client(*args, **kwargs))
except ImportError:  # pragma: nocover
    pass


class MemcachedClient(object):
    """ A wrapper around python-memcache Client in order to adapt
        cache contract.
    """

    def __init__(self, client):
        self.client = client

    def __enter__(self):  # pragma: nocover
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # pragma: nocover
        pass

    def set(self, key, value, time=0, namespace=None):
        """ Sets a key's value, regardless of previous contents
            in cache.
        """
        return self.client.set(key, value, time)

    def set_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Set multiple keys' values at once.
        """
        return self.client.set_multi(mapping, time, key_prefix)

    def add(self, key, value, time=0, namespace=None):
        """ Sets a key's value, if and only if the item is not
            already.
        """
        return self.client.add(key, value, time)

    def add_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Adds multiple values at once, with no effect for keys
            already in cache.
        """
        keys_failed = []
        client = self.client
        for key in mapping:
            if not client.add(key_prefix + key, mapping[key], time):
                keys_failed.append(key)
        return keys_failed

    def replace(self, key, value, time=0, namespace=None):
        """ Replaces a key's value, failing if item isn't already.
        """
        return self.client.replace(key, value, time)

    def replace_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Replaces multiple values at once, with no effect for
            keys not in cache.
        """
        keys_failed = []
        client = self.client
        for key in mapping:
            if not client.replace(key_prefix + key, mapping[key], time):
                keys_failed.append(key)
        return keys_failed

    def get(self, key, namespace=None):
        """ Looks up a single key.
        """
        return self.client.get(key)

    def get_multi(self, keys, key_prefix='', namespace=None):
        """ Looks up multiple keys from cache in one operation.
            This is the recommended way to do bulk loads.
        """
        return self.client.get_multi(keys, key_prefix)

    def delete(self, key, seconds=0, namespace=None):
        """ Deletes a key from cache.
        """
        return self.client.delete(key, seconds) == 1

    def delete_multi(self, keys, seconds=0, key_prefix='', namespace=None):
        """ Delete multiple keys at once.
        """
        return self.client.delete_multi(keys, seconds, key_prefix) == 1

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically increments a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then incremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.
        """
        result = self.client.incr(key, delta)
        if result is not None:
            return result
        if initial_value is None:
            return None
        self.client.add(key, initial_value)
        return self.client.incr(key, delta)

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically decrements a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then decremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.
        """
        result = self.client.decr(key, delta)
        if result is not None:
            return result
        if initial_value is None:
            return None
        self.client.add(key, initial_value)
        return self.client.decr(key, delta)

    def flush_all(self):
        """ Deletes everything in cache.
        """
        self.client.flush_all()
        return True
