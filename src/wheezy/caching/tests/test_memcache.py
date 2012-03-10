
"""
"""

from unittest import TestCase

from wheezy.caching.tests.test_cache import CacheTestMixin

try:
    from wheezy.caching.memcache import client_factory

    client = client_factory(['unix:/tmp/memcached.sock'])
    cache_factory = lambda: client

    class MemcacheClientTestCase(TestCase, CacheTestMixin):

        def setUp(self):
            self.context = cache_factory()
            self.client = self.context.__enter__()
            self.namespace = None

        def tearDown(self):
            self.client.flush_all()
            self.context.__exit__(None, None, None)

        def test_delete(self):
            assert self.client.delete('d')
            self.setget('d', 1)
            assert self.client.delete('d')

except ImportError:
    pass
