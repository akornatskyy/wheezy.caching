
""" Unit tests for ``wheezy.caching.pylibmc``.
"""

import os

from unittest import TestCase

from wheezy.caching.comp import Queue
from wheezy.caching.comp import xrange
from wheezy.caching.tests.test_cache import CacheTestMixin


try:
    from wheezy.caching.pylibmc import client_factory
except ImportError:  # pragma: nocover
    pass
else:
    from wheezy.caching.pylibmc import MemcachedClient

    class EagerPool(object):

        def __init__(self, create_factory, size):
            pool = Queue(size)
            for i in xrange(size):
                pool.put(create_factory())
            self.pool = pool
            self.acquire = pool.get
            self.get_back = pool.put

    client_pool = EagerPool(
        lambda: client_factory([
                os.environ.get('MEMCACHED_HOST', '127.0.0.1')
            ]), 1)

    class PylibmcClientTestCase(TestCase, CacheTestMixin):

        def setUp(self):
            self.client = MemcachedClient(client_pool)
            self.namespace = None

        def tearDown(self):
            self.client.flush_all()

        def test_delete_multi(self):
            mapping = {'d1': 1, 'd2': 2}
            keys = list(mapping.keys())
            assert not self.client.delete_multi(keys)
            self.setget_multi(mapping)
            assert self.client.delete_multi(keys)
