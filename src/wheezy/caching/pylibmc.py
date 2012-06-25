
""" ``pylibmc`` module.
"""

from wheezy.caching.encoding import encode_keys
from wheezy.caching.encoding import string_encode

try:
    c = __import__('pylibmc', None, None, ['Client', 'NotFound'])
    Client = c.Client
    NotFound = c.NotFound

    def client_factory(*args, **kwargs):
        """ Client factory for pylibmc.
        """
        key_encode = kwargs.pop('key_encode', None)
        kwargs.setdefault('binary', True)
        behaviors = kwargs.setdefault('behaviors', {})
        behaviors.setdefault('tcp_nodelay', True)
        behaviors.setdefault('ketama', True)
        return MemcachedClient(Client(*args, **kwargs), key_encode)

    del c
except ImportError:  # pragma: nocover
    pass


class MemcachedClient(object):
    """ A wrapper around pylibmc Client in order to adapt cache contract.
    """

    def __init__(self, client, key_encode):
        self.client = client
        self.key_encode = key_encode or string_encode

    def set(self, key, value, time=0, namespace=None):
        """ Sets a key's value, regardless of previous contents
            in cache.
        """
        return self.client.set(self.key_encode(key), value, time)

    def set_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Set multiple keys' values at once.
        """
        key_encode = self.key_encode
        keys, mapping = encode_keys(mapping, key_encode)
        failed = self.client.set_multi(mapping, time, key_encode(key_prefix))
        return failed and [keys[key] for key in failed] or failed

    def add(self, key, value, time=0, namespace=None):
        """ Sets a key's value, if and only if the item is not
            already.
        """
        return self.client.add(self.key_encode(key), value, time)

    def add_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Adds multiple values at once, with no effect for keys
            already in cache.
        """
        key_encode = self.key_encode
        keys, mapping = encode_keys(mapping, key_encode)
        failed = self.client.add_multi(mapping, time, key_encode(key_prefix))
        return failed and [keys[key] for key in failed] or failed

    def replace(self, key, value, time=0, namespace=None):
        """ Replaces a key's value, failing if item isn't already.
        """
        try:
            return self.client.replace(self.key_encode(key), value, time)
        except NotFound:
            return False

    def replace_multi(self, mapping, time=0, key_prefix='', namespace=None):
        """ Replaces multiple values at once, with no effect for
            keys not in cache.
        """
        key_encode = self.key_encode
        failed = []
        client = self.client
        for key in mapping:
            try:
                client.replace(
                    key_encode(key_prefix + key), mapping[key], time)
            except NotFound:
                failed.append(key)
        return failed

    def get(self, key, namespace=None):
        """ Looks up a single key.
        """
        return self.client.get(self.key_encode(key))

    def get_multi(self, keys, key_prefix='', namespace=None):
        """ Looks up multiple keys from cache in one operation.
            This is the recommended way to do bulk loads.
        """
        key_encode = self.key_encode
        encoded_keys = map(key_encode, keys)
        mapping = self.client.get_multi(encoded_keys, key_encode(key_prefix))
        if mapping:
            key_mapping = dict(zip(encoded_keys, keys))
            return dict([(key_mapping[key], mapping[key]) for key in mapping])
        return mapping

    def delete(self, key, seconds=0, namespace=None):
        """ Deletes a key from cache.
        """
        return self.client.delete(self.key_encode(key))

    def delete_multi(self, keys, seconds=0, key_prefix='', namespace=None):
        """ Delete multiple keys at once.
        """
        key_encode = self.key_encode
        return self.client.delete_multi(
            map(key_encode, keys), key_encode(key_prefix))

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        """ Atomically increments a key's value. The value, if too
            large, will wrap around.

            If the key does not yet exist in the cache and you specify
            an initial_value, the key's value will be set to this
            initial value and then incremented. If the key does not
            exist and no initial_value is specified, the key's value
            will not be set.
        """
        key = self.key_encode(key)
        try:
            return self.client.incr(key, delta)
        except NotFound:
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
        key = self.key_encode(key)
        try:
            return self.client.decr(key, delta)
        except NotFound:
            if initial_value is None:
                return None
            self.client.add(key, initial_value)
            return self.client.decr(key, delta)

    def flush_all(self):
        """ Deletes everything in cache.
        """
        self.client.flush_all()
        return True
