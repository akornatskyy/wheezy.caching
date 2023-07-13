""" ``pylibmc`` module.
"""

from wheezy.caching.encoding import encode_keys, string_encode

try:
    from pylibmc import Client, NotFound

    def client_factory(*args, **kwargs):
        """Client factory for pylibmc."""
        kwargs.setdefault("binary", True)
        behaviors = kwargs.setdefault("behaviors", {})
        behaviors.setdefault("tcp_nodelay", True)
        behaviors.setdefault("ketama", True)
        return Client(*args, **kwargs)

except ImportError:  # pragma: nocover
    import warnings

    warnings.warn("No module named 'pylibmc'", stacklevel=2)


class MemcachedClient(object):
    """A wrapper around pylibmc Client in order to adapt cache contract."""

    def __init__(self, pool, key_encode=None):
        assert hasattr(pool, "acquire")
        assert hasattr(pool, "get_back")
        self.pool = pool
        self.key_encode = key_encode or string_encode

    def set(self, key, value, time=0, namespace=None):
        """Sets a key's value, regardless of previous contents
        in cache.
        """
        key = self.key_encode(key)
        try:
            client = self.pool.acquire()
            return client.set(key, value, time)
        finally:
            self.pool.get_back(client)

    def set_multi(self, mapping, time=0, namespace=None):
        """Set multiple keys' values at once."""
        key_encode = self.key_encode
        keys, mapping = encode_keys(mapping, key_encode)
        try:
            client = self.pool.acquire()
            failed = client.set_multi(mapping, time)
        finally:
            self.pool.get_back(client)
        return failed and [keys[key] for key in failed] or failed

    def add(self, key, value, time=0, namespace=None):
        """Sets a key's value, if and only if the item is not
        already.
        """
        key = self.key_encode(key)
        try:
            client = self.pool.acquire()
            return client.add(key, value, time)
        finally:
            self.pool.get_back(client)

    def add_multi(self, mapping, time=0, namespace=None):
        """Adds multiple values at once, with no effect for keys
        already in cache.
        """
        key_encode = self.key_encode
        keys, mapping = encode_keys(mapping, key_encode)
        try:
            client = self.pool.acquire()
            failed = client.add_multi(mapping, time)
        finally:
            self.pool.get_back(client)
        return failed and [keys[key] for key in failed] or failed

    def replace(self, key, value, time=0, namespace=None):
        """Replaces a key's value, failing if item isn't already."""
        key = self.key_encode(key)
        try:
            try:
                client = self.pool.acquire()
                return client.replace(key, value, time)
            except NotFound:
                return False
        finally:
            self.pool.get_back(client)

    def replace_multi(self, mapping, time=0, namespace=None):
        """Replaces multiple values at once, with no effect for
        keys not in cache.
        """
        key_encode = self.key_encode
        failed = []
        mapping = [(key, key_encode(key), mapping[key]) for key in mapping]
        try:
            client = self.pool.acquire()
            for key, key_encoded, value in mapping:
                try:
                    client.replace(key_encoded, value, time)
                except NotFound:
                    failed.append(key)
        finally:
            self.pool.get_back(client)
        return failed

    def get(self, key, namespace=None):
        """Looks up a single key."""
        key = self.key_encode(key)
        try:
            client = self.pool.acquire()
            return client.get(key)
        finally:
            self.pool.get_back(client)

    def get_multi(self, keys, namespace=None):
        """Looks up multiple keys from cache in one operation.
        This is the recommended way to do bulk loads.
        """
        key_encode = self.key_encode
        encoded_keys = list(map(key_encode, keys))
        try:
            client = self.pool.acquire()
            mapping = client.get_multi(encoded_keys)
        finally:
            self.pool.get_back(client)
        if mapping:
            key_mapping = dict(zip(encoded_keys, keys))
            return dict([(key_mapping[key], mapping[key]) for key in mapping])
        return mapping

    def delete(self, key, seconds=0, namespace=None):
        """Deletes a key from cache."""
        key = self.key_encode(key)
        try:
            client = self.pool.acquire()
            return client.delete(key)
        finally:
            self.pool.get_back(client)

    def delete_multi(self, keys, seconds=0, namespace=None):
        """Delete multiple keys at once."""
        key_encode = self.key_encode
        keys = map(key_encode, keys)
        try:
            client = self.pool.acquire()
            return client.delete_multi(keys)
        finally:
            self.pool.get_back(client)

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
        try:
            client = self.pool.acquire()
            try:
                return client.incr(key, delta)
            except NotFound:
                if initial_value is None:
                    return None
                client.add(key, initial_value)
                return client.incr(key, delta)
        finally:
            self.pool.get_back(client)

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
        try:
            client = self.pool.acquire()
            try:
                return client.decr(key, delta)
            except NotFound:
                if initial_value is None:
                    return None
                client.add(key, initial_value)
                return client.decr(key, delta)
        finally:
            self.pool.get_back(client)

    def flush_all(self):
        """Deletes everything in cache."""
        try:
            client = self.pool.acquire()
            client.flush_all()
        finally:
            self.pool.get_back(client)
        return True
