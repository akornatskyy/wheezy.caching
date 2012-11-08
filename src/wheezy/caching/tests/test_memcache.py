
""" Unit tests for ``wheezy.caching.memcache``.
"""

from unittest import TestCase

from wheezy.caching.tests.test_cache import CacheTestMixin
from wheezy.caching.memcache import Client


if Client:
    from wheezy.caching.memcache import MemcachedClient

    class MemcacheClientTestCase(TestCase, CacheTestMixin):

        def setUp(self):
            self.client = MemcachedClient(['unix:/tmp/memcached.sock'])
            self.namespace = None

        def tearDown(self):
            self.client.flush_all()

        def test_delete(self):
            assert self.client.delete('d')
            self.setget('d', 1)
            assert self.client.delete('d')
