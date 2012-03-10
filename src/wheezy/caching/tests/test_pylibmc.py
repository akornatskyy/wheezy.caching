
"""
"""

from unittest import TestCase

from wheezy.caching.tests.test_cache import CacheTestMixin

try:
    from wheezy.caching.pools import EagerPool
    from wheezy.caching.pools import Pooled
    from wheezy.caching.pylibmc import client_factory

    client_pool = EagerPool(lambda: client_factory(['/tmp/memcached.sock']), 1)
    cache_factory = lambda: Pooled(client_pool)

    class PylibmcClientTestCase(TestCase, CacheTestMixin):

        def setUp(self):
            self.context = cache_factory()
            self.client = self.context.__enter__()
            self.namespace = None

        def tearDown(self):
            self.client.flush_all()
            self.context.__exit__(None, None, None)

        def test_delete_multi(self):
            mapping = {'d1': 1, 'd2': 2}
            keys = list(mapping.keys())
            assert not self.client.delete_multi(keys)
            self.setget_multi(mapping)
            assert self.client.delete_multi(keys)

except ImportError:
    pass
