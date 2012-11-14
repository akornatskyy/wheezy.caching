
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
