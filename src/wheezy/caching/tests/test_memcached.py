
"""
"""

from unittest import TestCase


class MemcachedClientTestMixin(object):

    def setget(self, key, value):
        assert self.client.set(key, value, 10) == True
        assert value == self.client.get(key)

    def setget_multi(self, mapping):
        assert self.client.set_multi(mapping, 10) == []
        keys = list(mapping.keys())
        values = self.client.get_multi(keys)
        for key in keys:
            assert mapping[key] == values[key]

    def test_getset(self):
        self.setget('s1', 'some string')
        self.setget('i1', 100)

    def test_getset_multi(self):
        self.setget_multi({'k1': 'v1', 'k2': 'v2'})

    def test_add(self):
        assert self.client.add('a', 100)
        assert 100 == self.client.get('a')
        assert not self.client.add('a', 100)

    def test_add_multi(self):
        mapping = {'a1': 1, 'a2': 2}
        assert self.client.add_multi(mapping) == []
        assert mapping == self.client.get_multi(['a1', 'a2'])
        assert self.client.add_multi(mapping) == ['a1', 'a2']

    def test_replace(self):
        assert self.client.add('r', 100)
        assert 100 == self.client.get('r')
        assert self.client.replace('r', 101)
        assert 101 == self.client.get('r')
        assert not self.client.replace('rr', 101)

    def test_replace_multi(self):
        mapping = {'r1': 1, 'r2': 2}
        assert self.client.replace_multi(mapping) == ['r1', 'r2']
        assert self.client.add_multi(mapping) == []
        mapping = {'r1': 100, 'r2': 200}
        assert self.client.replace_multi(mapping) == []
        assert mapping == self.client.get_multi(['r1', 'r2'])

    def test_delete(self):
        assert not self.client.delete('d')
        self.setget('d', 1)
        assert self.client.delete('d')

    def test_delete_multi(self):
        mapping = {'d1': 1, 'd2': 2}
        keys = list(mapping.keys())
        assert self.client.delete_multi(keys)
        self.setget_multi(mapping)
        assert self.client.delete_multi(keys)

    def test_incr(self):
        assert 1 == self.client.incr('ci', initial_value=0)
        assert 2 == self.client.incr('ci')

    def test_incr_returns_none(self):
        assert self.client.incr('ix') is None

    def test_decr(self):
        assert 9 == self.client.decr('cd', initial_value=10)
        assert 8 == self.client.decr('cd')

    def test_decr_none(self):
        assert self.client.decr('dx') is None

    def test_flush_all(self):
        mapping = {'s1': 1, 's2': 2}
        assert self.client.set_multi(mapping) == []
        assert self.client.flush_all()


from wheezy.caching.memory import MemoryCache

memory = MemoryCache()
memory_factory = lambda: memory


class MemoryCacheTestCase(TestCase, MemcachedClientTestMixin):

    def setUp(self):
        self.context = memory_factory()
        self.client = self.context.__enter__()

    def tearDown(self):
        self.client.flush_all()
        self.context.__exit__(None, None, None)


try:
    from wheezy.caching.memcache import client_factory as memcache_client

    memcache = memcache_client(['unix:/tmp/memcached.sock'])
    memcache_factory = lambda: memcache

    class MemcacheClientTestCase(TestCase, MemcachedClientTestMixin):

        def setUp(self):
            self.context = memcache_factory()
            self.client = self.context.__enter__()

        def tearDown(self):
            self.client.flush_all()
            self.context.__exit__(None, None, None)

        def test_delete(self):
            assert self.client.delete('d')
            self.setget('d', 1)
            assert self.client.delete('d')

except ImportError:
    pass

try:
    from wheezy.caching.pools import EagerPool
    from wheezy.caching.pools import Pooled
    from wheezy.caching.pylibmc import client_factory as pylibmc_client

    pool = EagerPool(lambda: pylibmc_client(['/tmp/memcached.sock']), 2)
    pylibmc_factory = lambda: Pooled(pool)

    class PylibmcClientTestCase(TestCase, MemcachedClientTestMixin):

        def setUp(self):
            self.context = pylibmc_factory()
            self.client = self.context.__enter__()

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
