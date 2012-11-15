
""" Unit tests for ``wheezy.caching.patterns``.
"""

import unittest

from mock import ANY
from mock import Mock
from mock import patch


class CachedTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.caching.patterns import Cached
        self.mock_cache = Mock()
        self.mock_dependency = Mock()
        self.cached = Cached(self.mock_cache, time=10, namespace='ns')

    def test_set(self):
        """ Ensure set operation is passed to cache.
        """
        self.cached.set('key', 'value')
        self.mock_cache.set.assert_called_once_with('key', 'value', 10, 'ns')

    def test_set_with_dependency(self):
        """ Ensure set operation is passed to cache and
            key added to dependency.
        """
        self.cached.set('key', 'value', self.mock_dependency)
        self.mock_cache.set.assert_called_once_with('key', 'value', 10, 'ns')
        self.mock_dependency.add.assert_called_once_with('key', 'ns')

    def test_set_multi(self):
        """ Ensure set_multi operation is passed to cache.
        """
        self.cached.set_multi({'key': 'value'}, 'key_prefix')
        self.mock_cache.set_multi.assert_called_once_with(
            {'key': 'value'}, 10, 'key_prefix', 'ns')

    def test_add(self):
        """ Ensure add operation is passed to cache.
        """
        self.cached.add('key', 'value')
        self.mock_cache.add.assert_called_once_with('key', 'value', 10, 'ns')

    def test_add_failed_with_dependency(self):
        """ Ensure add operation is passed to cache and
            key added to dependency.
        """
        self.mock_cache.add.return_value = False
        self.cached.add('key', 'value', self.mock_dependency)
        self.mock_cache.add.assert_called_once_with('key', 'value', 10, 'ns')
        assert not self.mock_dependency.add.called

    def test_add_with_dependency(self):
        """ Ensure add operation is passed to cache and
            key added to dependency.
        """
        self.cached.add('key', 'value', self.mock_dependency)
        self.mock_cache.add.assert_called_once_with('key', 'value', 10, 'ns')
        self.mock_dependency.add.assert_called_once_with('key', 'ns')

    def test_add_multi(self):
        """ Ensure add_multi operation is passed to cache.
        """
        self.cached.add_multi({'key': 'value'}, 'key_prefix')
        self.mock_cache.add_multi.assert_called_once_with(
            {'key': 'value'}, 10, 'key_prefix', 'ns')

    def test_replace(self):
        """ Ensure replace operation is passed to cache.
        """
        self.cached.replace('key', 'value')
        self.mock_cache.replace.assert_called_once_with(
            'key', 'value', 10, 'ns')

    def test_replace_multi(self):
        """ Ensure replace_multi operation is passed to cache.
        """
        self.cached.replace_multi({'key': 'value'}, 'key_prefix')
        self.mock_cache.replace_multi.assert_called_once_with(
            {'key': 'value'}, 10, 'key_prefix', 'ns')

    def test_get(self):
        """ Ensure get operation is passed to cache.
        """
        self.cached.get('key')
        self.mock_cache.get.assert_called_once_with('key', 'ns')

    def test_get_multi(self):
        """ Ensure get_multi operation is passed to cache.
        """
        self.cached.get_multi(['key'], 'key_prefix')
        self.mock_cache.get_multi.assert_called_once_with(
            ['key'], 'key_prefix', 'ns')

    def test_delete(self):
        """ Ensure delete operation is passed to cache.
        """
        self.cached.delete('key', 0)
        self.mock_cache.delete.assert_called_once_with('key', 0, 'ns')

    def test_delete_multi(self):
        """ Ensure delete_multi operation is passed to cache.
        """
        self.cached.delete_multi(['key'], 0, 'key_prefix')
        self.mock_cache.delete_multi.assert_called_once_with(
            ['key'], 0, 'key_prefix', 'ns')

    def test_incr(self):
        """ Ensure incr operation is passed to cache.
        """
        self.cached.incr('key', 1, 0)
        self.mock_cache.incr.assert_called_once_with('key', 1, 'ns', 0)

    def test_decr(self):
        """ Ensure decr operation is passed to cache.
        """
        self.cached.decr('key', 1, 0)
        self.mock_cache.decr.assert_called_once_with('key', 1, 'ns', 0)


class OnePassTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.caching.patterns import OnePass
        self.mock_cache = Mock()
        self.one_pass = OnePass(self.mock_cache, 'key',
                                time=10, namespace='ns')

    def test_enter(self):
        """ Enter returns one_pass instance.
        """
        self.mock_cache.add.return_value = True
        assert self.one_pass == self.one_pass.__enter__()
        assert self.one_pass.acquired
        self.mock_cache.add.assert_called_once_with('key', ANY, 10, 'ns')

    def test_exit_acquired(self):
        """ Releases key if acquired.
        """
        self.mock_cache.add.return_value = True
        self.one_pass.__enter__()
        assert self.one_pass.acquired
        self.one_pass.__exit__(None, None, None)
        self.mock_cache.delete.assert_called_once_with('key', 'ns')
        assert not self.one_pass.acquired

    def test_exit_not_acquired(self):
        """ If one pass was not acquired, do not release key.
        """
        self.mock_cache.add.return_value = False
        self.one_pass.__enter__()
        assert not self.one_pass.acquired
        self.one_pass.__exit__(None, None, None)
        assert not self.mock_cache.delete.called

    @patch('wheezy.caching.patterns.sleep')
    def test_wait_no_marker(self, mock_sleep):
        """ Exit wait loop if there is no marker.
        """
        self.mock_cache.add.return_value = False
        self.one_pass.__enter__()
        assert not self.one_pass.acquired
        self.mock_cache.get.return_value = None
        assert True == self.one_pass.wait()

    @patch('wheezy.caching.patterns.sleep')
    def test_wait_timeout(self, mock_sleep):
        """ Exit wait loop if there is timeout reached.
        """
        self.mock_cache.add.return_value = False
        self.one_pass.__enter__()
        assert not self.one_pass.acquired
        self.mock_cache.get.return_value = 1
        assert False == self.one_pass.wait()


class GetOrAddTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_add(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        cached = Cached(self.mock_cache, time=10, namespace='ns')
        return cached.get_or_add('key', self.mock_create_factory,
                                 dependency_factory)

    def test_found(self):
        """ An item found in cache.
        """
        self.mock_cache.get.return_value = 'x'
        assert 'x' == self.get_or_add()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        assert not self.mock_create_factory.called

    def test_create_none(self):
        """ Create factory returned None.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = None

        assert not self.get_or_add()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        self.mock_create_factory.assert_called_once_with()
        assert not self.mock_cache.add.called

    def test_add_failed(self):
        """ Attempt to add a value to cache failed.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = 'x'
        self.mock_cache.add.return_value = False

        assert 'x' == self.get_or_add()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        self.mock_cache.add.assert_called_once_with('key', 'x', 10, 'ns')

    def test_has_dependency(self):
        """ There is specified `dependency_factory`.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = 'x'
        self.mock_cache.add.return_value = True
        mock_dependency_factory = Mock()

        assert 'x' == self.get_or_add(mock_dependency_factory)
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        self.mock_cache.add.assert_called_once_with('key', 'x', 10, 'ns')
        mock_dependency_factory.return_value.add.assert_called_once_with(
            'key', 'ns')


class WrapsGetOrAddTestCase(GetOrAddTestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_add(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        kb = lambda f: lambda *args, **kwargs: 'key'
        cached = Cached(self.mock_cache, kb, time=10, namespace='ns')
        return cached.wraps_get_or_add(self.mock_create_factory)()

    def test_has_dependency(self):
        """ Not supported.
        """
        pass


class GetOrSetTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_set(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        cached = Cached(self.mock_cache, time=10, namespace='ns')
        return cached.get_or_set('key', self.mock_create_factory,
                                 dependency_factory)

    def test_found(self):
        """ An item found in cache.
        """
        self.mock_cache.get.return_value = 'x'
        assert 'x' == self.get_or_set()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        assert not self.mock_create_factory.called

    def test_create_none(self):
        """ Create factory returned None.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = None

        assert not self.get_or_set()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        self.mock_create_factory.assert_called_once_with()
        assert not self.mock_cache.add.called

    def test_no_dependency(self):
        """ There is specified `dependency_factory`.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = 'x'
        self.mock_cache.set.return_value = True

        assert 'x' == self.get_or_set()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        self.mock_cache.set.assert_called_once_with('key', 'x', 10, 'ns')

    def test_has_dependency(self):
        """ There is specified `dependency_factory`.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = 'x'
        self.mock_cache.set.return_value = True
        mock_dependency_factory = Mock()

        assert 'x' == self.get_or_set(mock_dependency_factory)
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        self.mock_cache.set.assert_called_once_with('key', 'x', 10, 'ns')
        mock_dependency_factory.return_value.add.assert_called_once_with(
            'key', 'ns')


class WrapsGetOrSetTestCase(GetOrSetTestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_set(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        kb = lambda f: lambda *args, **kwargs: 'key'
        cached = Cached(self.mock_cache, kb, time=10, namespace='ns')
        return cached.wraps_get_or_set(self.mock_create_factory)()

    def test_has_dependency(self):
        """ Not supported.
        """
        pass


class CachedCallTestCase(GetOrSetTestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_set(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        kb = lambda f: lambda *args, **kwargs: 'key'
        cached = Cached(self.mock_cache, kb, time=10, namespace='ns')
        return cached(self.mock_create_factory)()

    def test_has_dependency(self):
        """ Not supported.
        """
        pass


class OnePassCreateTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def one_pass_create(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        cached = Cached(self.mock_cache, time=10, namespace='ns', timeout=5)
        return cached.one_pass_create('key', self.mock_create_factory,
                                      dependency_factory)

    def test_create_none(self):
        """ One pass has been entered and create factory returns None.
        """
        self.mock_cache.add.return_value = True
        self.mock_create_factory.return_value = None
        assert not self.one_pass_create()

        self.mock_cache.add.assert_called_once_with(
            'one_pass:key', ANY, 5, 'ns')
        self.mock_create_factory.assert_called_once_with()
        assert not self.mock_cache.set.called
        self.mock_cache.delete.assert_called_once_with('one_pass:key', 'ns')

    def test_no_dependency(self):
        """ Create factory returned value.
        """
        self.mock_cache.add.return_value = True
        self.mock_create_factory.return_value = 'x'
        assert 'x' == self.one_pass_create()

        self.mock_cache.add.assert_called_once_with(
            'one_pass:key', ANY, 5, 'ns')
        self.mock_create_factory.assert_called_once_with()
        self.mock_cache.set.assert_called_once_with('key', 'x', 10, 'ns')
        self.mock_cache.delete.assert_called_once_with('one_pass:key', 'ns')

    def test_with_dependency(self):
        """ Create factory returned value.
        """
        self.mock_cache.add.return_value = True
        self.mock_create_factory.return_value = 'x'
        mock_dependency_factory = Mock()
        assert 'x' == self.one_pass_create(mock_dependency_factory)

        self.mock_cache.add.assert_called_once_with(
            'one_pass:key', ANY, 5, 'ns')
        self.mock_create_factory.assert_called_once_with()
        self.mock_cache.set.assert_called_once_with('key', 'x', 10, 'ns')
        self.mock_cache.delete.assert_called_once_with('one_pass:key', 'ns')
        mock_dependency_factory.return_value.add.assert_called_once_with(
            'key', 'ns')

    @patch('wheezy.caching.patterns.OnePass')
    def test_wait_timedout(self, mock_cls_one_pass):
        """ Wait on one pass has timed out.
        """
        mock_one_pass = mock_cls_one_pass.return_value
        self.mock_cache.add.return_value = False
        mock_one_pass.acquired = False
        mock_one_pass.wait.return_value = False

        assert not self.one_pass_create()

    @patch('wheezy.caching.patterns.OnePass')
    def test_wait_get(self, mock_cls_one_pass):
        """ Wait on one pass succeed, get value.
        """
        mock_one_pass = mock_cls_one_pass.return_value
        self.mock_cache.add.return_value = False
        mock_one_pass.acquired = False
        mock_one_pass.wait.return_value = True
        self.mock_cache.get.return_value = 'x'

        assert 'x' == self.one_pass_create()


class GetOrCreateTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_create(self):
        from wheezy.caching.patterns import Cached
        cached = Cached(self.mock_cache, time=10, namespace='ns', timeout=5)
        return cached.get_or_create('key', self.mock_create_factory)

    def test_found(self):
        """ An item found in cache.
        """
        self.mock_cache.get.return_value = 'x'
        assert 'x' == self.get_or_create()
        self.mock_cache.get.assert_called_once_with('key', 'ns')
        assert not self.mock_create_factory.called

    def test_not_found(self):
        """ Not found in cache.
        """
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = 'x'
        assert 'x' == self.get_or_create()
        self.mock_cache.get.assert_called_once_with('key', 'ns')


class WrapsGetOrCreateTestCase(GetOrCreateTestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_create(self, dependency_factory=None):
        from wheezy.caching.patterns import Cached
        kb = lambda f: lambda *args, **kwargs: 'key'
        cached = Cached(self.mock_cache, kb, time=10, namespace='ns',
                        timeout=5)
        return cached.wraps_get_or_create(self.mock_create_factory)()


class KeyBuilderTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.caching.patterns import key_builder
        self.mk = key_builder('prefix')

    def test_noargs(self):
        def items():
            pass
        assert 'prefix-items' == self.mk(items)()

    def test_args(self):
        def items(x, y):
            pass
        assert "prefix-items:'None':None" == self.mk(items)('None', None)

    def test_defaults(self):
        def items(x, y=''):
            pass
        assert "prefix-items:1:''" == self.mk(items)(1)
        assert "prefix-items:1:'s'" == self.mk(items)(1, y='s')
        assert "prefix-items:1:2" == self.mk(items)(1, y=2)

    def test_sepecial(self):
        def items(cls, y):
            pass
        assert 'prefix-items:1' == self.mk(items)('cls', 1)
        assert 'prefix-items:None' == self.mk(items)('cls', None)
        assert "prefix-items:''" == self.mk(items)('cls', '')
