
"""
"""

from unittest import TestCase

from wheezy.caching.memory import MemoryCache
from wheezy.caching.tests.test_cache import CacheTestMixin


cache = MemoryCache()
cache_factory = lambda: cache


class MemoryCacheTestCase(TestCase, CacheTestMixin):

    def setUp(self):
        self.context = cache_factory()
        self.client = self.context.__enter__()
        self.namespace = None

    def tearDown(self):
        self.client.flush_all()
        self.context.__exit__(None, None, None)
