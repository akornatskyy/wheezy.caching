
""" Unit tests for ``wheezy.caching.patterns``.
"""

import unittest

from mock import ANY
from mock import Mock


class CacheDependencyTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.caching.dependency import CacheDependency
        self.mock_cache = Mock()
        self.d = CacheDependency(self.mock_cache, 'key',
                                 time=10, namespace='default')

    def test_next_key(self):
        """ Ensures consistency of key issued.
        """
        self.mock_cache.incr.return_value = 1
        assert 'key1' == self.d.next_key()
        self.mock_cache.incr.assert_called_once_with('key', 1, 'default', 0)

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 2
        assert 'key2' == self.d.next_key('ns')
        self.mock_cache.incr.assert_called_once_with('key', 1, 'ns', 0)

    def test_next_keys(self):
        """ Ensures consistency of keys issued.
        """
        self.mock_cache.incr.return_value = 2
        assert ['key1', 'key2'] == self.d.next_keys(2)
        self.mock_cache.incr.assert_called_once_with('key', 2, 'default', 0)

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 4
        assert ['key3', 'key4'] == self.d.next_keys(2, 'ns')
        self.mock_cache.incr.assert_called_once_with('key', 2, 'ns', 0)

    def test_add(self):
        """ Ensure dependency is added.
        """
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add('k')
        self.mock_cache.add.assert_called_once_with(
            'key1', 'k', 10, 'default')

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add('k', 'ns')
        self.mock_cache.add.assert_called_once_with(
            'key1', 'k', 10, 'ns')

    def test_add_multi(self):
        """ Ensure multiple dependency keys added.
        """
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add_multi(['k'])
        self.mock_cache.add_multi.assert_called_once_with(
            {'key1': 'k'}, 10, '', 'default')

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add_multi(['k'], 'prefix-')
        self.mock_cache.add_multi.assert_called_once_with(
            {'key1': 'prefix-k'}, 10, '', 'default')

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add_multi(['k'], namespace='ns')
        self.mock_cache.add_multi.assert_called_once_with(
            {'key1': 'k'}, 10, '', 'ns')

    def test_delete(self):
        """ Ensure related keys are invalidated.
        """
        self.mock_cache.get.return_value = None
        assert self.d.delete()
        self.mock_cache.get.assert_called_once_with(
            'key', 'default')

        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = None
        assert self.d.delete('ns')
        self.mock_cache.get.assert_called_once_with(
            'key', 'ns')

        def side_effect(*args):
            assert ['key1', 'key2'] == args[0]
            return {'key1': 'k1', 'key2': 'k2'}
        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = 2
        self.mock_cache.get_multi.side_effect = side_effect
        assert self.d.delete()
        self.mock_cache.get.assert_called_once_with(
            'key', 'default')
        self.mock_cache.get_multi.assert_called_once_with(
            ANY, '', 'default')
        self.mock_cache.delete_multi.assert_called_once_with(
            ANY, 0, '', 'default')
        assert ['k1', 'k2', 'key', 'key1', 'key2'] == sorted(
            self.mock_cache.delete_multi.call_args[0][0])
