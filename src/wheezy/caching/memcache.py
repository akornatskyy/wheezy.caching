""" ``memcache`` module.
"""

from wheezy.caching.encoding import encode_keys, string_encode

try:
    from memcache import Client
except ImportError:  # pragma: nocover
    Client = None
    import warnings

    warnings.warn("No module named 'memcache'", stacklevel=2)


class MemcachedClient(object):
    """A wrapper around python-memcache Client in order to adapt
    cache contract.
    """

    def __init__(self, *args, **kwargs):
        self.key_encode = kwargs.pop("key_encode", string_encode)
        if Client is None:  # pragma: nocover
            raise ImportError("No module named 'memcache'")
        self.client = Client(*args, **kwargs)

    def set(self, key, value, time=0, namespace=None):
        """Sets a key's value, regardless of previous contents
        in cache.
        """
        return self.client.set(self.key_encode(key), value, time)

    def set_multi(self, mapping, time=0, namespace=None):
        """Set multiple keys' values at once."""
        key_encode = self.key_encode
        keys, mapping = encode_keys(mapping, key_encode)
        failed = self.client.set_multi(mapping, time)
        return failed and [keys[key] for key in failed] or failed

    def add(self, key, value, time=0, namespace=None):
        """Sets a key's value, if and only if the item is not
        already.
        """
        return self.client.add(self.key_encode(key), value, time)

    def add_multi(self, mapping, time=0, namespace=None):
        """Adds multiple values at once, with no effect for keys
        already in cache.
        """
        failed = []
        key_encode = self.key_encode
        client = self.client
        for key in mapping:
            if not client.add(key_encode(key), mapping[key], time):
                failed.append(key)
        return failed

    def replace(self, key, value, time=0, namespace=None):
        """Replaces a key's value, failing if item isn't already."""
        return self.client.replace(self.key_encode(key), value, time)

    def replace_multi(self, mapping, time=0, namespace=None):
        """Replaces multiple values at once, with no effect for
        keys not in cache.
        """
        failed = []
        key_encode = self.key_encode
        client = self.client
        for key in mapping:
            if not client.replace(key_encode(key), mapping[key], time):
                failed.append(key)
        return failed

    def get(self, key, namespace=None):
        """Looks up a single key."""
        return self.client.get(self.key_encode(key))

    def get_multi(self, keys, namespace=None):
        """Looks up multiple keys from cache in one operation.
        This is the recommended way to do bulk loads.
        """
        key_encode = self.key_encode
        encoded_keys = list(map(key_encode, keys))
        mapping = self.client.get_multi(encoded_keys)
        if mapping:
            key_mapping = dict(zip(encoded_keys, keys))
            return dict([(key_mapping[key], mapping[key]) for key in mapping])
        return mapping

    def delete(self, key, seconds=0, namespace=None):
        """Deletes a key from cache."""
        return self.client.delete(self.key_encode(key), seconds) == 1

    def delete_multi(self, keys, seconds=0, namespace=None):
        """Delete multiple keys at once."""
        return (
            self.client.delete_multi(map(self.key_encode, keys), seconds) == 1
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
        key = self.key_encode(key)
        result = self.client.incr(key, delta)
        if result is not None:
            return result
        if initial_value is None:
            return None
        self.client.add(key, initial_value)
        return self.client.incr(key, delta)

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        """Atomically decrements a key's value. The value, if too
        large, will wrap around.

        If the key does not yet exist in the cache and you specify
        an initial_value, the key's value will be set to this
        initial value and then decremented. If the key does not
        exist and no initial_value is specified, the key's value
        will not be set.
        """
        key = self.key_encode(key)
        result = self.client.decr(key, delta)
        if result is not None:
            return result
        if initial_value is None:
            return None
        self.client.add(key, initial_value)
        return self.client.decr(key, delta)

    def flush_all(self):
        """Deletes everything in cache."""
        self.client.flush_all()
        return True
