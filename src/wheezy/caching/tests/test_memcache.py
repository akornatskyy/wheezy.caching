import os
from unittest import TestCase

from wheezy.caching.memcache import Client
from wheezy.caching.tests.test_cache import CacheTestMixin

if Client:
    from wheezy.caching.memcache import MemcachedClient

    class MemcacheClientTestCase(TestCase, CacheTestMixin):
        def setUp(self):
            self.client = MemcachedClient(
                [os.environ.get("MEMCACHED_HOST", "127.0.0.1")]
            )
            self.namespace = None

        def tearDown(self):
            self.client.flush_all()

        def test_delete(self):
            assert self.client.delete("d")
            self.setget("d", 1)
            assert self.client.delete("d")
