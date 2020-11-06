""" Unit tests for ``wheezy.caching``.
"""


class CacheTestMixin(object):
    def setget(self, key, value):
        assert self.client.set(key, value, 10, self.namespace) is True
        assert value == self.client.get(key, self.namespace)

    def setget_multi(self, mapping):
        assert self.client.set_multi(mapping, 10, self.namespace) == []
        keys = list(mapping.keys())
        values = self.client.get_multi(keys, self.namespace)
        for key in keys:
            assert mapping[key] == values[key]

    def test_get_notfound(self):
        assert self.client.get("uknown", self.namespace) is None

    def test_get_multi_some_found(self):
        self.setget("s1", "some string")
        assert {"s1": "some string"} == self.client.get_multi(
            ["unknown1", "s1"], namespace=self.namespace
        )

    def test_get_multi_notfound(self):
        assert {} == self.client.get_multi(
            ["unknown1", "unknown2"], namespace=self.namespace
        )

    def test_getset(self):
        self.setget("s1", "some string")
        self.setget("i1", 100)

    def test_getset_unicode_keys(self):
        self.setget("s1", "some string")
        self.setget("i1", 100)

    def test_getset_multi(self):
        self.setget_multi({"k1": "v1", "k2": "v2"})

    def test_getset_multi_unicode_keys(self):
        self.setget_multi({"k1": "v1", "k2": "v2"})

    def test_add(self):
        assert self.client.add("a", 100, namespace=self.namespace)
        assert 100 == self.client.get("a", namespace=self.namespace)
        assert not self.client.add("a", 100, namespace=self.namespace)

    def test_add_multi(self):
        mapping = {"a1": 1, "a2": 2}
        assert self.client.add_multi(mapping, namespace=self.namespace) == []
        assert mapping == self.client.get_multi(
            ["a1", "a2"], namespace=self.namespace
        )
        assert ["a1", "a2"] == sorted(
            self.client.add_multi(mapping, namespace=self.namespace)
        )

    def test_replace(self):
        assert self.client.add("r", 100, namespace=self.namespace)
        assert 100 == self.client.get("r", namespace=self.namespace)
        assert self.client.replace("r", 101, namespace=self.namespace)
        assert 101 == self.client.get("r", namespace=self.namespace)
        assert not self.client.replace("rr", 101, namespace=self.namespace)

    def test_replace_multi(self):
        mapping = {"r1": 1, "r2": 2}
        assert ["r1", "r2"] == sorted(
            self.client.replace_multi(mapping, namespace=self.namespace)
        )
        assert [] == self.client.add_multi(mapping, namespace=self.namespace)
        mapping = {"r1": 100, "r2": 200}
        assert [] == self.client.replace_multi(
            mapping, namespace=self.namespace
        )
        assert mapping == self.client.get_multi(
            ["r1", "r2"], namespace=self.namespace
        )

    def test_delete(self):
        assert not self.client.delete("d", namespace=self.namespace)
        self.setget("d", 1)
        assert self.client.delete("d", namespace=self.namespace)
        assert not self.client.get("d", self.namespace)

    def test_delete_multi(self):
        mapping = {"d1": 1, "d2": 2}
        keys = list(mapping.keys())
        assert self.client.delete_multi(keys, namespace=self.namespace)
        self.setget_multi(mapping)
        assert self.client.delete_multi(keys, namespace=self.namespace)
        assert not self.client.get_multi(keys, self.namespace)

    def test_incr(self):
        assert 1 == self.client.incr(
            "ci", namespace=self.namespace, initial_value=0
        )
        assert 1 == self.client.get("ci", namespace=self.namespace)
        assert 2 == self.client.incr("ci", namespace=self.namespace)
        assert 2 == self.client.get("ci", namespace=self.namespace)

    def test_incr_returns_none(self):
        assert self.client.incr("ix", namespace=self.namespace) is None

    def test_decr(self):
        assert 9 == self.client.decr(
            "cd", namespace=self.namespace, initial_value=10
        )
        assert 9 == self.client.get("cd", namespace=self.namespace)
        assert 8 == self.client.decr("cd", namespace=self.namespace)
        assert 8 == self.client.get("cd", namespace=self.namespace)

    def test_decr_none(self):
        assert self.client.decr("dx") is None

    def test_flush_all(self):
        mapping = {"s1": 1, "s2": 2}
        assert [] == self.client.set_multi(mapping, namespace=self.namespace)
        assert self.client.flush_all()
