
""" ``patterns`` module.
"""

from time import sleep
from time import time


def get_or_add(key, create_factory, dependency_factory=None,
               time=0, namespace=None, cache=None):
    """ Cache Pattern: get an item by *key* from *cache* and
        if it is not available use *create_factory* to aquire one.
        If result is not `None` use cache `add` operation to store
        result and if operation succeed use *dependency_factory*
        to get an instance of `CacheDependency` to add *key* to it.
    """
    result = cache.get(key, namespace)
    if result is not None:
        return result
    result = create_factory()
    if result is not None:
        succeed = cache.add(key, result, time, namespace)
        if succeed and dependency_factory is not None:
            dependency = dependency_factory()
            dependency.add(key, namespace)
    return result


def partial_get_or_add(cache, time=0, namespace=None,
                       timeout=10, key_prefix='one_pass:'):
    """ Specializes `get_or_add` cache pattern to::

            get_or_add(key, create_factory, dependency_factory=None)
    """
    def get_or_add_wrapper(key, create_factory, dependency_factory=None):
        return get_or_add(
            key, create_factory, dependency_factory,
            time, namespace, cache)
    return get_or_add_wrapper


def get_or_set(key, create_factory, dependency_factory=None,
               time=0, namespace=None, cache=None):
    """ Cache Pattern: get an item by *key* from *cache* and
        if it is not available use *create_factory* to aquire one.
        If result is not `None` use cache `set` operation to store
        result and use *dependency_factory* to get an instance of
        `CacheDependency` to add *key* to it.
    """
    result = cache.get(key, namespace)
    if result is not None:
        return result
    result = create_factory()
    if result is not None:
        cache.set(key, result, time, namespace)
        if dependency_factory is not None:
            dependency = dependency_factory()
            dependency.add(key, namespace)
    return result


def partial_get_or_set(cache, time=0, namespace=None,
                       timeout=10, key_prefix='one_pass:'):
    """ Specializes `get_or_set` cache pattern to::

            get_or_set(key, create_factory, dependency_factory=None)
    """
    def get_or_set_wrapper(key, create_factory, dependency_factory=None):
        return get_or_set(
            key, create_factory, dependency_factory,
            time, namespace, cache)
    return get_or_set_wrapper


def one_pass_create(key, create_factory, dependency_factory=None,
                    time=0, namespace=None, cache=None,
                    timeout=10, key_prefix='one_pass:'):
    """ Cache Pattern: try enter one pass: (1) if entered
        use *create_factory* to get a value if result is not `None`
        use cache `set` operation to store result and use
        *dependency_factory* to get an instance of `CacheDependency`
        to add *key* to it; (2) if not entered `wait` until one
        pass is available and it is not timed out get an item by *key*
        from *cache*.
    """
    result = None
    one_pass = OnePass(cache, key_prefix + key, timeout, namespace)
    try:
        one_pass.__enter__()
        if one_pass.acquired:
            result = create_factory()
            if result is not None:
                cache.set(key, result, time, namespace)
                if dependency_factory is not None:
                    dependency = dependency_factory()
                    dependency.add(key, namespace)
        elif one_pass.wait():
            result = cache.get(key, namespace)
    finally:
        one_pass.__exit__(None, None, None)
    return result


def partial_one_pass_create(cache, time=0, namespace=None,
                            timeout=10, key_prefix='one_pass:'):
    """ Specializes `one_pass_create` cache pattern to::

            one_pass_create(key, create_factory, dependency_factory=None)
    """
    def one_pass_create_wrapper(key, create_factory, dependency_factory=None):
        return one_pass_create(
            key, create_factory, dependency_factory,
            time, namespace, cache,
            timeout, key_prefix)
    return one_pass_create_wrapper


def get_or_create(key, create_factory, dependency_factory=None,
                  time=0, namespace=None, cache=None,
                  timeout=10, key_prefix='one_pass:'):
    """ Cache Pattern: get an item by *key* from *cache* and
        if it is not available see `one_pass_create`.
    """
    result = cache.get(key, namespace)
    if result is not None:
        return result
    return one_pass_create(key, create_factory, dependency_factory,
                           time, namespace, cache, timeout, key_prefix)


def partial_get_or_create(cache, time=0, namespace=None,
                          timeout=10, key_prefix='one_pass:'):
    """ Specializes `get_or_create` cache pattern to::

            get_or_create(key, create_factory, dependency_factory=None)
    """
    def get_or_create_wrapper(key, create_factory, dependency_factory=None):
        result = cache.get(key, namespace)
        if result is not None:
            return result
        return one_pass_create(
            key, create_factory, dependency_factory,
            time, namespace, cache,
            timeout, key_prefix)
    return get_or_create_wrapper


class OnePass(object):
    """ A solution to `Thundering Head` problem.

        see http://en.wikipedia.org/wiki/Thundering_herd_problem

        Typical use::

            with OnePass(cache, 'op:' + key) as one_pass:
                if one_pass.acquired:
                    # update *key* in cache
                elif one_pass.wait():
                    # obtain *key* from cache
                else:
                    # timeout
    """

    __slots__ = ('cache', 'key', 'time', 'namespace', 'acquired')

    def __init__(self, cache, key, time=10, namespace=None):
        self.cache = cache
        self.key = key
        self.time = time
        self.namespace = namespace
        self.acquired = False

    def __enter__(self):
        marker = int(time())
        self.acquired = self.cache.add(self.key, marker, self.time,
                                       self.namespace)
        return self

    def wait(self, timeout=None):
        """ Wait *timeout* seconds for the one pass become available.

            *timeout* - if not passed defaults to *time* used during
            initialization.
        """
        assert not self.acquired
        expected = marker = self.cache.get(self.key, self.namespace)
        timeout = timeout or self.time
        wait_time = 0.05
        while timeout > 0.0 and expected == marker:
            sleep(wait_time)
            marker = self.cache.get(self.key, self.namespace)
            if marker is None:  # deleted or timed out
                return True
            if wait_time < 0.8:
                wait_time *= 2.0
            timeout -= wait_time
        return False

    def __exit__(self, exc_type, exc_value, traceback):
        if self.acquired:
            self.cache.delete(self.key, self.namespace)
            self.acquired = False
