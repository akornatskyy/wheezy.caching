""" Unit tests for ``wheezy.caching.patterns``.
"""

import unittest
from unittest.mock import ANY, Mock

from wheezy.caching.dependency import CacheDependency


class CacheDependencyTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.d = CacheDependency(self.mock_cache, time=10, namespace="ns")

    def test_next_key(self):
        """Ensures consistency of key issued."""
        self.mock_cache.incr.return_value = 1
        assert "key1" == self.d.next_key("key")
        self.mock_cache.incr.assert_called_once_with("key", 1, "ns", 0)

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 2
        assert "key2" == self.d.next_key("key")
        self.mock_cache.incr.assert_called_once_with("key", 1, "ns", 0)

    def test_next_keys(self):
        """Ensures consistency of keys issued."""
        self.mock_cache.incr.return_value = 2
        assert ["key1", "key2"] == self.d.next_keys("key", 2)
        self.mock_cache.incr.assert_called_once_with("key", 2, "ns", 0)

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 4
        assert ["key3", "key4"] == self.d.next_keys("key", 2)
        self.mock_cache.incr.assert_called_once_with("key", 2, "ns", 0)

    def test_add(self):
        """Ensure dependency is added."""
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add("key", "k")
        self.mock_cache.add.assert_called_once_with("key1", "k", 10, "ns")

    def test_add_multi(self):
        """Ensure multiple dependency keys added."""
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True
        assert self.d.add_multi("key", ["k"])
        self.mock_cache.add_multi.assert_called_once_with(
            {"key1": "k"}, 10, "ns"
        )

        self.mock_cache.reset_mock()
        self.mock_cache.incr.return_value = 1
        self.mock_cache.add.return_value = True

    def test_get_keys(self):
        """Ensure related keys are returned."""
        self.mock_cache.get.return_value = None
        assert [] == self.d.get_keys("key")
        self.mock_cache.get.assert_called_once_with("key", "ns")
        assert not self.mock_cache.get_multi.called

        def side_effect(*args):
            assert ["key1", "key2"] == args[0]
            return {"key1": "k1", "key2": "k2"}

        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = 2
        self.mock_cache.get_multi.side_effect = side_effect
        keys = self.d.get_keys("key")
        assert ["k1", "k2", "key", "key1", "key2"] == sorted(keys)
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_cache.get_multi.assert_called_once_with(ANY, "ns")

    def test_get_multi(self):
        """Ensure related keys are returned for multi
        dependencies.
        """
        self.mock_cache.get_multi.return_value = None
        assert [] == self.d.get_multi_keys(["ka", "kb"])
        self.mock_cache.get_multi.assert_called_once_with(["ka", "kb"], "ns")

        calls = [{"ka": 2, "kb": 1}, {"ka1": "k1", "ka2": "k2", "kb1": "k3"}]

        def side_effect(*args):
            result = calls[0]
            del calls[0]
            return result

        self.mock_cache.reset_mock()
        self.mock_cache.get_multi.side_effect = side_effect

        keys = self.d.get_multi_keys(["ka", "kb", "kc"])
        assert [
            "k1",
            "k2",
            "k3",
            "ka",
            "ka1",
            "ka2",
            "kb",
            "kb1",
            "kc",
        ] == sorted(keys)
        assert 2 == self.mock_cache.get_multi.call_count

    def test_delete(self):
        """Ensure related keys are invalidated."""
        self.mock_cache.get.return_value = None
        assert self.d.delete("key")
        self.mock_cache.get.assert_called_once_with("key", "ns")
        assert not self.mock_cache.get_multi.called
        assert not self.mock_cache.delete_multi.called

        def side_effect(*args):
            assert ["key1", "key2"] == args[0]
            return {"key1": "k1", "key2": "k2"}

        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = 2
        self.mock_cache.get_multi.side_effect = side_effect
        assert self.d.delete("key")
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_cache.get_multi.assert_called_once_with(ANY, "ns")
        self.mock_cache.delete_multi.assert_called_once_with(ANY, 0, "ns")
        assert ["k1", "k2", "key", "key1", "key2"] == sorted(
            self.mock_cache.delete_multi.call_args[0][0]
        )

    def test_delete_multi(self):
        """Ensure related keys are invalidated for multi
        dependencies.
        """
        self.mock_cache.get_multi.return_value = None
        assert self.d.delete_multi(["ka", "kb"])
        self.mock_cache.get_multi.assert_called_once_with(["ka", "kb"], "ns")
        assert not self.mock_cache.delete_multi.called

        calls = [{"ka": 2, "kb": 1}, {"ka1": "k1", "ka2": "k2", "kb1": "k3"}]

        def side_effect(*args):
            result = calls[0]
            del calls[0]
            return result

        self.mock_cache.reset_mock()
        self.mock_cache.get_multi.side_effect = side_effect

        assert self.d.delete_multi(["ka", "kb", "kc"])
        assert 2 == self.mock_cache.get_multi.call_count
        self.mock_cache.delete_multi.assert_called_once_with(ANY, 0, "ns")
        assert [
            "k1",
            "k2",
            "k3",
            "ka",
            "ka1",
            "ka2",
            "kb",
            "kb1",
            "kc",
        ] == sorted(self.mock_cache.delete_multi.call_args[0][0])
