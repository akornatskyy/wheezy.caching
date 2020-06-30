""" Unit tests for ``wheezy.caching.memory``.
"""

from unittest import TestCase

from wheezy.caching.memory import MemoryCache
from wheezy.caching.tests.test_cache import CacheTestMixin


class MemoryCacheTestCase(TestCase, CacheTestMixin):
    def setUp(self):
        self.client = MemoryCache()
        self.namespace = None

    def tearDown(self):
        self.client.flush_all()
