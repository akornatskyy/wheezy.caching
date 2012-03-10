
"""
"""

from unittest import TestCase

from wheezy.caching.client import CacheClient
from wheezy.caching.memory import MemoryCache
from wheezy.caching.tests.test_cache import CacheTestMixin


cache1 = MemoryCache()
cache2 = MemoryCache()
cache_client = CacheClient(namespaces={
        'cache1': lambda: cache1,
        'cache2': lambda: cache2
    },
    default_namespace='cache1')
cache_factory = lambda: cache_client


class CacheClientDefaultTestCase(TestCase, CacheTestMixin):

    def setUp(self):
        self.context = cache_factory()
        self.client = self.context.__enter__()
        self.namespace = None

    def tearDown(self):
        self.client.flush_all()
        self.context.__exit__(None, None, None)


class CacheClientDefaultByNameTestCase(TestCase, CacheTestMixin):

    def setUp(self):
        self.context = cache_factory()
        self.client = self.context.__enter__()
        self.namespace = 'cache1'

    def tearDown(self):
        self.client.flush_all()
        self.context.__exit__(None, None, None)


class CacheClientByNamespaceTestCase(TestCase, CacheTestMixin):

    def setUp(self):
        self.context = cache_factory()
        self.client = self.context.__enter__()
        self.namespace = 'cache2'

    def tearDown(self):
        self.client.flush_all()
        self.context.__exit__(None, None, None)
