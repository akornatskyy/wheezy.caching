
""" ``interface`` module.
"""


class NullCache(object):

    def __init__(self):
        pass

    def set(self, key, value, time=0):
        """ Sets a key's value, regardless of previous contents
            in cache.

            >>> c = NullCache()
            >>> c.set('k', 'v')
            True
        """
        return True

    def set_multi(self, mapping, time=0, key_prefix=''):
        """ Set multiple keys' values at once.

            >>> c = NullCache()
            >>> c.set_multi({})
            []
        """
        return []

    def add(self, key, value, time=0):
        """ Sets a key's value, if and only if the item is not
            already.

            >>> c = NullCache()
            >>> c.add('k', 'v')
            True
        """
        return True

    def add_multi(self, mapping, time=0, key_prefix=''):
        """ Adds multiple values at once, with no effect for keys
            already in cache.

            >>> c = NullCache()
            >>> c.add_multi({})
            []
        """
        return []

    def replace(self, key, value, time=0):
        """ Replaces a key's value, failing if item isn't already.

            >>> c = NullCache()
            >>> c.replace('k', 'v')
            True
        """
        return True

    def replace_multi(self, mapping, time=0, key_prefix=''):
        """ Replaces multiple values at once, with no effect for
            keys not in cache.

            >>> c = NullCache()
            >>> c.replace_multi({})
            []
        """
        return []

    def get(self, key, namespace=None):
        """
            Looks up a single key.

            >>> c = NullCache()
            >>> c.get('k')
        """
        return None

    def get_multi(self, keys, key_prefix=''):
        """
            Looks up multiple keys from cache in one operation.
            This is the recommended way to do bulk loads.

            >>> c = NullCache()
            >>> c.get_multi([])
            {}
        """
        return {}

    def delete(self, key, seconds=0):
        """
            Deletes a key from cache.

            >>> c = NullCache()
            >>> c.delete('k')
            True
        """
        return True

    def delete_multi(self, keys, seconds=0, key_prefix=''):
        """
            Delete multiple keys at once.

            >>> c = NullCache()
            >>> c.delete_multi([])
            True
        """
        return True

    def flush_all(self):
        """
            Deletes everything in cache.

            >>> c = NullCache()
            >>> c.flush_all()
            True
        """
        return True
