
""" Unit tests for ``wheezy.caching.logging``.
"""

import unittest

from mock import Mock


class OnePassHandlerTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.caching.logging import OnePassHandler
        self.mock_inner = Mock()
        self.mock_cache = Mock()
        self.h = OnePassHandler(self.mock_inner, self.mock_cache, 60)

    def test_emit_first_call(self):
        """ Ensure the inner handler emit on first call.
        """
        mock_record = Mock()
        mock_record.getMessage.return_value = 'msg'
        self.mock_cache.add.return_value = True
        self.h.emit(mock_record)
        assert self.mock_cache.add.called
        self.mock_inner.emit.assert_called_once(mock_record)

    def test_emit_next_call(self):
        """ Ensure there is no call to inner handler emit on next call.
        """
        mock_record = Mock()
        mock_record.getMessage.return_value = 'msg'
        self.mock_cache.add.return_value = False
        self.h.emit(mock_record)
        assert self.mock_cache.add.called
        assert not self.mock_inner.emit.called
