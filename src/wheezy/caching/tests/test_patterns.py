
""" Unit tests for ``wheezy.caching.patterns``.
"""

import unittest

from mock import ANY
from mock import Mock
from mock import patch


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
        from wheezy.caching.patterns import get_or_add as ga
        return ga('key', self.mock_create_factory, dependency_factory,
                  10, 'ns', self.mock_cache)

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


class GetOrSetTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_set(self, dependency_factory=None):
        from wheezy.caching.patterns import get_or_set as gs
        return gs('key', self.mock_create_factory, dependency_factory,
                  10, 'ns', self.mock_cache)

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
