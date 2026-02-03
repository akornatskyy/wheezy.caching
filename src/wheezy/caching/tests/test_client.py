from unittest import TestCase

from wheezy.caching.client import CacheClient
from wheezy.caching.memory import MemoryCache
from wheezy.caching.tests.test_cache import CacheTestMixin

cache1 = MemoryCache()
cache2 = MemoryCache()
client = CacheClient(
    namespaces={"cache1": cache1, "cache2": cache2}, default_namespace="cache1"
)


class CacheClientDefaultTestCase(TestCase, CacheTestMixin):
    def setUp(self):
        self.client = client
        self.namespace = None

    def tearDown(self):
        self.client.flush_all()


class CacheClientDefaultByNameTestCase(TestCase, CacheTestMixin):
    def setUp(self):
        self.client = client
        self.namespace = "cache1"

    def tearDown(self):
        self.client.flush_all()


class CacheClientByNamespaceTestCase(TestCase, CacheTestMixin):
    def setUp(self):
        self.client = client
        self.namespace = "cache2"

    def tearDown(self):
        self.client.flush_all()
