""" Unit tests for ``wheezy.caching.patterns``.
"""

import unittest
from unittest.mock import ANY, Mock, patch

from wheezy.caching.patterns import Cached, OnePass, key_builder


class CachedTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_dependency = Mock()
        self.cached = Cached(self.mock_cache, time=10, namespace="ns")
        self.cached.dependency = self.mock_dependency

    def test_set(self):
        """Ensure set operation is passed to cache."""
        self.cached.set("key", "value")
        self.mock_cache.set.assert_called_once_with("key", "value", 10, "ns")

    def test_set_with_dependency(self):
        """Ensure set operation is passed to cache and
        key added to dependency.
        """
        self.cached.set("key", "value", "master_key")
        self.mock_cache.set.assert_called_once_with("key", "value", 10, "ns")
        self.mock_dependency.add.assert_called_once_with("master_key", "key")

    def test_set_multi(self):
        """Ensure set_multi operation is passed to cache."""
        self.cached.set_multi({"key": "value"})
        self.mock_cache.set_multi.assert_called_once_with(
            {"key": "value"}, 10, "ns"
        )

    def test_add(self):
        """Ensure add operation is passed to cache."""
        self.cached.add("key", "value")
        self.mock_cache.add.assert_called_once_with("key", "value", 10, "ns")

    def test_add_failed_with_dependency(self):
        """Ensure add operation is passed to cache and
        key added to dependency.
        """
        self.mock_cache.add.return_value = False
        self.cached.add("key", "value", self.mock_dependency)
        self.mock_cache.add.assert_called_once_with("key", "value", 10, "ns")
        assert not self.mock_dependency.add.called

    def test_add_with_dependency(self):
        """Ensure add operation is passed to cache and
        key added to dependency.
        """
        self.cached.add("key", "value", "master_key")
        self.mock_cache.add.assert_called_once_with("key", "value", 10, "ns")
        self.mock_dependency.add.assert_called_once_with("master_key", "key")

    def test_add_multi(self):
        """Ensure add_multi operation is passed to cache."""
        self.cached.add_multi({"key": "value"})
        self.mock_cache.add_multi.assert_called_once_with(
            {"key": "value"}, 10, "ns"
        )

    def test_replace(self):
        """Ensure replace operation is passed to cache."""
        self.cached.replace("key", "value")
        self.mock_cache.replace.assert_called_once_with(
            "key", "value", 10, "ns"
        )

    def test_replace_multi(self):
        """Ensure replace_multi operation is passed to cache."""
        self.cached.replace_multi({"key": "value"})
        self.mock_cache.replace_multi.assert_called_once_with(
            {"key": "value"}, 10, "ns"
        )

    def test_get(self):
        """Ensure get operation is passed to cache."""
        self.cached.get("key")
        self.mock_cache.get.assert_called_once_with("key", "ns")

    def test_get_multi(self):
        """Ensure get_multi operation is passed to cache."""
        self.cached.get_multi(["key"])
        self.mock_cache.get_multi.assert_called_once_with(["key"], "ns")

    def test_delete(self):
        """Ensure delete operation is passed to cache."""
        self.cached.delete("key", 0)
        self.mock_cache.delete.assert_called_once_with("key", 0, "ns")

    def test_delete_multi(self):
        """Ensure delete_multi operation is passed to cache."""
        self.cached.delete_multi(["key"], 0)
        self.mock_cache.delete_multi.assert_called_once_with(["key"], 0, "ns")

    def test_incr(self):
        """Ensure incr operation is passed to cache."""
        self.cached.incr("key", 1, 0)
        self.mock_cache.incr.assert_called_once_with("key", 1, "ns", 0)

    def test_decr(self):
        """Ensure decr operation is passed to cache."""
        self.cached.decr("key", 1, 0)
        self.mock_cache.decr.assert_called_once_with("key", 1, "ns", 0)

    def test_dependency(self):
        """Ensure returned CacheDependency is properly initialized."""
        cached = Cached(self.mock_cache, time=10, namespace="ns")
        d = cached.dependency
        assert cached.cache == d.cache
        assert cached.time == d.time
        assert cached.namespace == d.namespace

    def test_adapt_make_key(self):
        """Adapts make_key to function args."""

        def make_key():
            return "key"

        def my_func():
            pass  # pragma: nocover

        mk = self.cached.adapt(my_func, make_key)
        assert "key" == mk()

    def test_adapt_make_key_cls(self):
        """Ignore 'cls' argument."""

        def make_key():
            return "key"

        def my_func(cls):
            pass  # pragma: nocover

        mk = self.cached.adapt(my_func, make_key)
        assert "key" == mk("cls")


class OnePassTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.one_pass = OnePass(
            self.mock_cache, "key", time=10, namespace="ns"
        )

    def test_enter(self):
        """Enter returns one_pass instance."""
        self.mock_cache.add.return_value = True
        assert self.one_pass == self.one_pass.__enter__()
        assert self.one_pass.acquired
        self.mock_cache.add.assert_called_once_with("key", ANY, 10, "ns")

    def test_exit_acquired(self):
        """Releases key if acquired."""
        self.mock_cache.add.return_value = True
        self.one_pass.__enter__()
        assert self.one_pass.acquired
        self.one_pass.__exit__(None, None, None)
        self.mock_cache.delete.assert_called_once_with("key", 0, "ns")
        assert not self.one_pass.acquired

    def test_exit_not_acquired(self):
        """If one pass was not acquired, do not release key."""
        self.mock_cache.add.return_value = False
        self.one_pass.__enter__()
        assert not self.one_pass.acquired
        self.one_pass.__exit__(None, None, None)
        assert not self.mock_cache.delete.called

    @patch("wheezy.caching.patterns.sleep")
    def test_wait_no_marker(self, mock_sleep):
        """Exit wait loop if there is no marker."""
        self.mock_cache.add.return_value = False
        self.one_pass.__enter__()
        assert not self.one_pass.acquired
        self.mock_cache.get.return_value = None
        assert self.one_pass.wait()

    @patch("wheezy.caching.patterns.sleep")
    def test_wait_timeout(self, mock_sleep):
        """Exit wait loop if there is timeout reached."""
        self.mock_cache.add.return_value = False
        self.one_pass.__enter__()
        assert not self.one_pass.acquired
        self.mock_cache.get.return_value = 1
        assert not self.one_pass.wait()


class GetOrAddTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()
        self.mock_dependency = Mock()

    def get_or_add(self, dependency_key_factory=None):
        cached = Cached(self.mock_cache, time=10, namespace="ns")
        cached.dependency = self.mock_dependency
        return cached.get_or_add(
            "key", self.mock_create_factory, dependency_key_factory
        )

    def test_found(self):
        """An item found in cache."""
        self.mock_cache.get.return_value = "x"
        assert "x" == self.get_or_add()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        assert not self.mock_create_factory.called

    def test_create_none(self):
        """Create factory returned None."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = None

        assert not self.get_or_add()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_create_factory.assert_called_once_with()
        assert not self.mock_cache.add.called

    def test_add_failed(self):
        """Attempt to add a value to cache failed."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = "x"
        self.mock_cache.add.return_value = False

        assert "x" == self.get_or_add()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_cache.add.assert_called_once_with("key", "x", 10, "ns")

    def test_has_dependency(self):
        """There is specified `dependency_factory`."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = "x"
        self.mock_cache.add.return_value = True
        mock_dependency_key_factory = Mock()
        mock_dependency_key_factory.return_value = "master_key"

        assert "x" == self.get_or_add(mock_dependency_key_factory)
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_cache.add.assert_called_once_with("key", "x", 10, "ns")
        self.mock_dependency.add.assert_called_once_with("master_key", "key")


class WrapsGetOrAddTestCase(GetOrAddTestCase):
    def test_has_dependency(self):
        pass

    def get_or_add(self, dependency_factory=None):
        def kb(f):
            def key(*args, **kwargs):
                return "key"

            return key

        cached = Cached(self.mock_cache, kb, time=10, namespace="ns")
        return cached.wraps_get_or_add(self.mock_create_factory)()


class WrapsGetOrAddMakeKeyTestCase(WrapsGetOrAddTestCase):
    def get_or_add(self, dependency_factory=None):
        cached = Cached(self.mock_cache, time=10, namespace="ns")

        @cached.wraps_get_or_add(make_key=lambda: "key")
        def create_factory():
            return self.mock_create_factory()

        return create_factory()


class GetOrSetTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()
        self.mock_dependency = Mock()

    def get_or_set(self, dependency_key_factory=None):
        cached = Cached(self.mock_cache, time=10, namespace="ns")
        cached.dependency = self.mock_dependency
        return cached.get_or_set(
            "key", self.mock_create_factory, dependency_key_factory
        )

    def test_found(self):
        """An item found in cache."""
        self.mock_cache.get.return_value = "x"
        assert "x" == self.get_or_set()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        assert not self.mock_create_factory.called

    def test_create_none(self):
        """Create factory returned None."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = None

        assert not self.get_or_set()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_create_factory.assert_called_once_with()
        assert not self.mock_cache.add.called

    def test_no_dependency(self):
        """There is specified `dependency_factory`."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = "x"
        self.mock_cache.set.return_value = True

        assert "x" == self.get_or_set()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_cache.set.assert_called_once_with("key", "x", 10, "ns")

    def test_has_dependency(self):
        """There is specified `dependency_factory`."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = "x"
        self.mock_cache.set.return_value = True
        mock_dependency_key_factory = Mock()
        mock_dependency_key_factory.return_value = "master_key"

        assert "x" == self.get_or_set(mock_dependency_key_factory)
        self.mock_cache.get.assert_called_once_with("key", "ns")
        self.mock_cache.set.assert_called_once_with("key", "x", 10, "ns")
        self.mock_dependency.add.assert_called_once_with("master_key", "key")


class WrapsGetOrSetTestCase(GetOrSetTestCase):
    def test_has_dependency(self):
        pass

    def get_or_set(self, dependency_factory=None):
        def kb(f):
            def key(*args, **kwargs):
                return "key"

            return key

        cached = Cached(self.mock_cache, kb, time=10, namespace="ns")
        return cached.wraps_get_or_set(self.mock_create_factory)()


class WrapsGetOrSetMakeKeyTestCase(WrapsGetOrSetTestCase):
    def get_or_set(self, dependency_factory=None):
        cached = Cached(self.mock_cache, time=10, namespace="ns")

        @cached.wraps_get_or_set(make_key=lambda: "key")
        def create_factory():
            return self.mock_create_factory()

        return create_factory()


class CachedCallTestCase(GetOrSetTestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_set(self, dependency_factory=None):
        def kb(f):
            def key(*args, **kwargs):
                return "key"

            return key

        cached = Cached(self.mock_cache, kb, time=10, namespace="ns")
        return cached(self.mock_create_factory)()

    def test_has_dependency(self):
        """Not supported."""


class OnePassCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()
        self.mock_dependency = Mock()

    def one_pass_create(self, dependency_key_factory=None):
        cached = Cached(self.mock_cache, time=10, namespace="ns", timeout=5)
        cached.dependency = self.mock_dependency
        return cached.one_pass_create(
            "key", self.mock_create_factory, dependency_key_factory
        )

    def test_create_none(self):
        """One pass has been entered and create factory returns None."""
        self.mock_cache.add.return_value = True
        self.mock_create_factory.return_value = None
        assert not self.one_pass_create()

        self.mock_cache.add.assert_called_once_with(
            "one_pass:key", ANY, 5, "ns"
        )
        self.mock_create_factory.assert_called_once_with()
        assert not self.mock_cache.set.called
        self.mock_cache.delete.assert_called_once_with("one_pass:key", 0, "ns")

    def test_no_dependency(self):
        """Create factory returned value."""
        self.mock_cache.add.return_value = True
        self.mock_create_factory.return_value = "x"
        assert "x" == self.one_pass_create()

        self.mock_cache.add.assert_called_once_with(
            "one_pass:key", ANY, 5, "ns"
        )
        self.mock_create_factory.assert_called_once_with()
        self.mock_cache.set.assert_called_once_with("key", "x", 10, "ns")
        self.mock_cache.delete.assert_called_once_with("one_pass:key", 0, "ns")

    def test_with_dependency(self):
        """Create factory returned value."""
        self.mock_cache.add.return_value = True
        self.mock_create_factory.return_value = "x"
        mock_dependency_key_factory = Mock()
        mock_dependency_key_factory.return_value = "master_key"
        assert "x" == self.one_pass_create(mock_dependency_key_factory)

        self.mock_cache.add.assert_called_once_with(
            "one_pass:key", ANY, 5, "ns"
        )
        self.mock_create_factory.assert_called_once_with()
        self.mock_cache.set.assert_called_once_with("key", "x", 10, "ns")
        self.mock_cache.delete.assert_called_once_with("one_pass:key", 0, "ns")
        self.mock_dependency.add.assert_called_once_with("master_key", "key")

    @patch("wheezy.caching.patterns.OnePass")
    def test_wait_timedout(self, mock_cls_one_pass):
        """Wait on one pass has timed out."""
        mock_one_pass = mock_cls_one_pass.return_value
        self.mock_cache.add.return_value = False
        mock_one_pass.acquired = False
        mock_one_pass.wait.return_value = False

        assert not self.one_pass_create()

    @patch("wheezy.caching.patterns.OnePass")
    def test_wait_get(self, mock_cls_one_pass):
        """Wait on one pass succeed, get value."""
        mock_one_pass = mock_cls_one_pass.return_value
        self.mock_cache.add.return_value = False
        mock_one_pass.acquired = False
        mock_one_pass.wait.return_value = True
        self.mock_cache.get.return_value = "x"

        assert "x" == self.one_pass_create()


class GetOrCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_create(self):
        cached = Cached(self.mock_cache, time=10, namespace="ns", timeout=5)
        return cached.get_or_create("key", self.mock_create_factory)

    def test_found(self):
        """An item found in cache."""
        self.mock_cache.get.return_value = "x"
        assert "x" == self.get_or_create()
        self.mock_cache.get.assert_called_once_with("key", "ns")
        assert not self.mock_create_factory.called

    def test_not_found(self):
        """Not found in cache."""
        self.mock_cache.get.return_value = None
        self.mock_create_factory.return_value = "x"
        assert "x" == self.get_or_create()
        self.mock_cache.get.assert_called_once_with("key", "ns")


class WrapsGetOrCreateTestCase(GetOrCreateTestCase):
    def get_or_create(self, dependency_factory=None):
        def kb(f):
            def key(*args, **kwargs):
                return "key"

            return key

        cached = Cached(
            self.mock_cache, kb, time=10, namespace="ns", timeout=5
        )
        return cached.wraps_get_or_create(self.mock_create_factory)()


class WrapsGetOrCreateMakeKeyTestCase(WrapsGetOrCreateTestCase):
    def get_or_create(self, dependency_factory=None):
        cached = Cached(self.mock_cache, time=10, namespace="ns")

        @cached.wraps_get_or_create(make_key=lambda: "key")
        def create_factory():
            return self.mock_create_factory()

        return create_factory()


class GetOrSetMultiTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_cache = Mock()
        self.mock_create_factory = Mock()

    def get_or_set_multi(self):
        def mk(i):
            return "k%d" % i

        cached = Cached(self.mock_cache, time=10, namespace="ns")
        r = cached.get_or_set_multi(mk, self.mock_create_factory, [1, 2])
        assert [(1, "a"), (2, "b")] == sorted(r.items())

    def test_all_cache_hit(self):
        """All items are taken from cache."""

        def get_multi(keys, namespace):
            assert ["k1", "k2"] == sorted(keys)
            return {"k1": "a", "k2": "b"}

        self.mock_cache.get_multi.side_effect = get_multi
        self.get_or_set_multi()
        assert not self.mock_create_factory.called

    def test_all_cache_miss(self):
        """All items are missed in cache."""

        def set_multi(keys, time, namespace):
            assert [("k1", "a"), ("k2", "b")] == sorted(keys.items())

        self.mock_cache.get_multi.return_value = {}
        self.mock_create_factory.return_value = {1: "a", 2: "b"}
        self.mock_cache.set_multi.side_effect = set_multi
        self.get_or_set_multi()
        self.mock_create_factory.assert_called_once_with([1, 2])
        assert self.mock_cache.set_multi.called

    def test_some_cache_miss(self):
        """Some items are missed in cache."""
        self.mock_cache.get_multi.return_value = {"k2": "b"}
        self.mock_create_factory.return_value = {1: "a"}
        self.get_or_set_multi()
        self.mock_create_factory.assert_called_once_with([1])
        self.mock_cache.set_multi.assert_called_once_with(
            {"k1": "a"}, 10, "ns"
        )

    def test_some_cache_miss_create_factory_no_result(self):
        """Some items are missed in cache and factory returns
        no results.
        """

        def mk(i):
            return "k%d" % i

        cached = Cached(self.mock_cache, time=10, namespace="ns")
        self.mock_cache.get_multi.return_value = {"k2": "b"}
        self.mock_create_factory.return_value = {}
        r = cached.get_or_set_multi(mk, self.mock_create_factory, [1, 2])
        assert [(2, "b")] == list(r.items())
        self.mock_create_factory.assert_called_once_with([1])
        assert not self.mock_cache.set_multi.called


class WrapsGetOrSetMultiTestCase(GetOrSetMultiTestCase):
    def get_or_set_multi(self):
        def mk(i):
            return "k%d" % i

        cached = Cached(self.mock_cache, time=10, namespace="ns")

        @cached.wraps_get_or_set_multi(make_key=mk)
        def create_factory(ids):
            return self.mock_create_factory(ids)

        r = create_factory([1, 2])
        assert [(1, "a"), (2, "b")] == sorted(r.items())


class WrapsGetOrSetMultiCtxTestCase(GetOrSetMultiTestCase):
    def get_or_set_multi(self):
        def mk(i):
            return "k%d" % i

        cached = Cached(self.mock_cache, time=10, namespace="ns")

        @cached.wraps_get_or_set_multi(make_key=mk)
        def create_factory(cls, ids):
            return self.mock_create_factory(ids)

        r = create_factory("cls", [1, 2])
        assert [(1, "a"), (2, "b")] == sorted(r.items())


class KeyBuilderTestCase(unittest.TestCase):
    def setUp(self):
        self.mk = key_builder("prefix")

    def test_noargs(self):
        def items():
            pass  # pragma: nocover

        assert "prefix-items" == self.mk(items)()

    def test_args(self):
        def items(x, y):
            pass  # pragma: nocover

        assert "prefix-items:'None':None" == self.mk(items)("None", None)

    def test_defaults(self):
        def items(x, y=""):
            pass  # pragma: nocover

        assert "prefix-items:1:''" == self.mk(items)(1)
        assert "prefix-items:1:'s'" == self.mk(items)(1, y="s")
        assert "prefix-items:1:2" == self.mk(items)(1, y=2)

    def test_sepecial(self):
        def items(cls, y):
            pass  # pragma: nocover

        assert "prefix-items:1" == self.mk(items)("cls", 1)
        assert "prefix-items:None" == self.mk(items)("cls", None)
        assert "prefix-items:''" == self.mk(items)("cls", "")

    def test_object(self):
        class Spec(object):
            def __init__(self, locale="en"):
                self.locale = locale

            def __repr__(self):
                return "<spec:%s>" % self.locale

        def items(spec):
            pass  # pragma: nocover

        assert "prefix-items:<spec:en>" == self.mk(items)(Spec())
