""" ``patterns`` module.
"""

from inspect import getfullargspec
from time import sleep, time

from wheezy.caching.dependency import CacheDependency
from wheezy.caching.utils import total_seconds


class Cached(object):
    """Specializes access to cache by using a number of common settings
    for various cache operations and patterns.
    """

    def __init__(
        self,
        cache,
        key_builder=None,
        time=0,
        namespace=None,
        timeout=10,
        key_prefix="one_pass:",
    ):
        self.cache = cache
        self.key_builder = key_builder
        self.time = total_seconds(time)
        self.namespace = namespace
        self.timeout = total_seconds(timeout)
        self.key_prefix = key_prefix
        self.dependency = CacheDependency(cache, time, namespace)

    def set(self, key, value, dependency_key=None):
        """Sets a key's value, regardless of previous contents
        in cache.
        """
        succeed = self.cache.set(key, value, self.time, self.namespace)
        if dependency_key:
            self.dependency.add(dependency_key, key)
        return succeed

    def set_multi(self, mapping):
        """Set multiple keys' values at once."""
        return self.cache.set_multi(mapping, self.time, self.namespace)

    def add(self, key, value, dependency_key=None):
        """Sets a key's value, if and only if the item is not
        already.
        """
        succeed = self.cache.add(key, value, self.time, self.namespace)
        if succeed and dependency_key:
            self.dependency.add(dependency_key, key)
        return succeed

    def add_multi(self, mapping):
        """Adds multiple values at once, with no effect for keys
        already in cache.
        """
        return self.cache.add_multi(mapping, self.time, self.namespace)

    def replace(self, key, value):
        """Replaces a key's value, failing if item isn't already."""
        return self.cache.replace(key, value, self.time, self.namespace)

    def replace_multi(self, mapping):
        """Replaces multiple values at once, with no effect for
        keys not in cache.
        """
        return self.cache.replace_multi(mapping, self.time, self.namespace)

    def get(self, key):
        """Looks up a single key."""
        return self.cache.get(key, self.namespace)

    def get_multi(self, keys):
        """Looks up multiple keys from cache in one operation.
        This is the recommended way to do bulk loads.
        """
        return self.cache.get_multi(keys, self.namespace)

    def delete(self, key, seconds=0):
        """Deletes a key from cache."""
        return self.cache.delete(key, seconds, self.namespace)

    def delete_multi(self, keys, seconds=0):
        """Delete multiple keys at once."""
        return self.cache.delete_multi(keys, seconds, self.namespace)

    def incr(self, key, delta=1, initial_value=None):
        """Atomically increments a key's value."""
        return self.cache.incr(key, delta, self.namespace, initial_value)

    def decr(self, key, delta=1, initial_value=None):
        """Atomically decrements a key's value."""
        return self.cache.decr(key, delta, self.namespace, initial_value)

    def get_or_add(self, key, create_factory, dependency_key_factory):
        """Cache Pattern: get an item by *key* from *cache* and
        if it is not available use *create_factory* to aquire one.
        If result is not `None` use cache `add` operation to store
        result and if operation succeed use *dependency_key_factory*
        to get an instance of `dependency_key` to link with *key*.
        """
        result = self.cache.get(key, self.namespace)
        if result is not None:
            return result
        result = create_factory()
        if result is not None:
            succeed = self.cache.add(key, result, self.time, self.namespace)
            if succeed and dependency_key_factory is not None:
                self.dependency.add(dependency_key_factory(), key)
        return result

    def wraps_get_or_add(self, wrapped=None, make_key=None):
        """Returns specialized decorator for `get_or_add` cache
        pattern.

        Example::

            kb = key_builder('repo')
            cached = Cached(cache, kb, time=60)

            @cached.wraps_get_or_add
            def list_items(self, locale):
                pass
        """

        def decorate(func):
            mk = self.adapt(func, make_key)

            def get_or_add_wrapper(*args, **kwargs):
                key = mk(*args, **kwargs)
                result = self.cache.get(key, self.namespace)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                if result is not None:
                    self.cache.add(key, result, self.time, self.namespace)
                return result

            return get_or_add_wrapper

        if wrapped is None:
            return decorate
        else:
            return decorate(wrapped)

    def get_or_set(self, key, create_factory, dependency_key_factory=None):
        """Cache Pattern: get an item by *key* from *cache* and
        if it is not available use *create_factory* to aquire one.
        If result is not `None` use cache `set` operation to store
        result and use *dependency_key_factory* to get an instance
        of `dependency_key` to link with *key*.
        """
        result = self.cache.get(key, self.namespace)
        if result is not None:
            return result
        result = create_factory()
        if result is not None:
            self.cache.set(key, result, self.time, self.namespace)
            if dependency_key_factory is not None:
                self.dependency.add(dependency_key_factory(), key)
        return result

    def __call__(self, wrapped=None, make_key=None):
        return self.wraps_get_or_set(wrapped, make_key)

    def wraps_get_or_set(self, wrapped=None, make_key=None):
        """Returns specialized decorator for `get_or_set` cache
        pattern.

        Example::

            kb = key_builder('repo')
            cached = Cached(cache, kb, time=60)

            @cached
            # or @cached.wraps_get_or_set
            def list_items(self, locale):
                pass
        """

        def decorate(func):
            mk = self.adapt(func, make_key)

            def get_or_set_wrapper(*args, **kwargs):
                key = mk(*args, **kwargs)
                result = self.cache.get(key, self.namespace)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                if result is not None:
                    self.cache.set(key, result, self.time, self.namespace)
                return result

            return get_or_set_wrapper

        if wrapped is None:
            return decorate
        else:
            return decorate(wrapped)

    def get_or_set_multi(self, make_key, create_factory, args):
        """Cache Pattern: `get_multi` items by *make_key* over
        *args* from *cache* and if there are any missing use
        *create_factory* to aquire them, if result available
        use cache `set_multi` operation to store results,
        return cached items if any.
        """
        key_map = dict((make_key(a), a) for a in args)
        cache_result = self.get_multi(key_map.keys())
        if not cache_result:
            data_result = create_factory(args)
        elif len(cache_result) != len(key_map):
            data_result = create_factory(
                [key_map[key] for key in key_map if key not in cache_result]
            )
        else:
            return dict(
                [(key_map[key], cache_result[key]) for key in cache_result]
            )

        if not data_result:
            return dict(
                [(key_map[key], cache_result[key]) for key in cache_result]
            )
        self.set_multi(
            dict(
                [
                    (key, data_result[k])
                    for key, k in key_map.items()
                    if k in data_result
                ]
            )
        )
        data_result.update(
            [(key_map[key], cache_result[key]) for key in cache_result]
        )
        return data_result

    def wraps_get_or_set_multi(self, make_key):
        """Returns specialized decorator for `get_or_set_multi` cache
        pattern.

        Example::

            cached = Cached(cache, kb, time=60)

            @cached.wraps_get_or_set_multi(
                make_key=lambda i: 'key:%r' % i)
            def get_multi_account(account_ids):
                pass
        """
        assert make_key

        def decorate(func):
            argnames = getfullargspec(func)[0]
            if argnames and argnames[0] in ("self", "cls", "klass"):
                assert len(argnames) == 2

                def get_or_set_multi_wrapper_with_ctx(ctx, args):
                    return self.get_or_set_multi(
                        make_key, lambda fargs: func(ctx, fargs), args
                    )

                return get_or_set_multi_wrapper_with_ctx
            else:
                assert len(argnames) == 1

                def get_or_set_multi_wrapper(args):
                    return self.get_or_set_multi(make_key, func, args)

                return get_or_set_multi_wrapper

        return decorate

    def one_pass_create(
        self, key, create_factory, dependency_key_factory=None
    ):
        """Cache Pattern: try enter one pass: (1) if entered
        use *create_factory* to get a value if result is not `None`
        use cache `set` operation to store result and use
        *dependency_key_factory* to get an instance of `dependency_key`
        to link with *key*; (2) if not entered `wait` until one pass is
        available and it is not timed out get an item by *key* from
        *cache*.
        """
        result = None
        one_pass = OnePass(
            self.cache, self.key_prefix + key, self.timeout, self.namespace
        )
        try:
            one_pass.__enter__()
            if one_pass.acquired:
                result = create_factory()
                if result is not None:
                    self.cache.set(key, result, self.time, self.namespace)
                    if dependency_key_factory is not None:
                        self.dependency.add(dependency_key_factory(), key)
            elif one_pass.wait():
                result = self.cache.get(key, self.namespace)
        finally:
            one_pass.__exit__(None, None, None)
        return result

    def get_or_create(self, key, create_factory, dependency_key_factory=None):
        """Cache Pattern: get an item by *key* from *cache* and
        if it is not available see `one_pass_create`.
        """
        result = self.cache.get(key, self.namespace)
        if result is not None:
            return result
        return self.one_pass_create(
            key, create_factory, dependency_key_factory
        )

    def wraps_get_or_create(self, wrapped=None, make_key=None):
        """Returns specialized decorator for `get_or_create` cache
        pattern.

        Example::

            kb = key_builder('repo')
            cached = Cached(cache, kb, time=60)

            @cached.wraps_get_or_create
            def list_items(self, locale):
                pass
        """

        def decorate(func):
            mk = self.adapt(func, make_key)

            def get_or_create_wrapper(*args, **kwargs):
                key = mk(*args, **kwargs)
                result = self.cache.get(key, self.namespace)
                if result is not None:
                    return result
                return self.one_pass_create(key, lambda: func(*args, **kwargs))

            return get_or_create_wrapper

        if wrapped is None:
            return decorate
        else:
            return decorate(wrapped)

    # region: internal details

    def adapt(self, func, make_key=None):
        if make_key:
            argnames = getfullargspec(func)[0]
            if argnames and argnames[0] in ("self", "cls", "klass"):
                return lambda ignore, *args, **kwargs: make_key(
                    *args, **kwargs
                )
            else:
                return make_key
        else:
            return self.key_builder(func)


class OnePass(object):
    """A solution to `Thundering Head` problem.

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

    __slots__ = ("cache", "key", "time", "namespace", "acquired")

    def __init__(self, cache, key, time=10, namespace=None):
        self.cache = cache
        self.key = key
        self.time = total_seconds(time)
        self.namespace = namespace
        self.acquired = False

    def __enter__(self):
        marker = int(time())
        self.acquired = self.cache.add(
            self.key, marker, self.time, self.namespace
        )
        return self

    def wait(self, timeout=None):
        """Wait *timeout* seconds for the one pass become available.

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
            self.cache.delete(self.key, 0, self.namespace)
            self.acquired = False


def key_format(func, key_prefix):
    """Returns a key format for *func* and *key_prefix*.

    >>> def list_items(self, locale='en', sort_order=1):
    ...     pass
    >>> key_format(list_items, 'repo')
    'repo-list_items:%r:%r'
    """
    argnames = getfullargspec(func)[0]
    n = len(argnames)
    if n and argnames[0] in ("self", "cls", "klass"):
        n -= 1
    return "%s-%s%s" % (key_prefix, func.__name__, ":%r" * n)


def key_formatter(key_prefix):
    """Specialize a key format with *key_prefix*.

    >>> def list_items(self, locale='en', sort_order=1):
    ...     pass
    >>> repo_key_format = key_formatter('repo')
    >>> repo_key_format(list_items)
    'repo-list_items:%r:%r'
    """

    def key_format_wrapper(func):
        return key_format(func, key_prefix)

    return key_format_wrapper


def key_builder(key_prefix=""):
    """Returns a key builder that allows build a make cache key
    function at runtime.

    >>> def list_items(self, locale='en', sort_order=1):
    ...     pass

    >>> repo_key_builder = key_builder('repo')
    >>> make_key = repo_key_builder(list_items)
    >>> make_key('self')
    "repo-list_items:'en':1"
    >>> make_key('self', 'uk')
    "repo-list_items:'uk':1"
    >>> make_key('self', sort_order=0)
    "repo-list_items:'en':0"

    Here is an example of make key function::

        def key_list_items(self, locale='en', sort_order=1):
            return "repo-list_items:%r:%r" % (locale, sort_order)

    """

    def build(func):
        spec = getfullargspec(func)
        argnames = spec.args
        defaults = spec.defaults
        if defaults:
            n = len(defaults)
            defaults = dict(zip(argnames[-n:], defaults))
            args = argnames[:-n]
            args.extend('%s=defaults["%s"]' % (n, n) for n in argnames[-n:])
        else:
            args = argnames
        if argnames and argnames[0] in ("self", "cls", "klass"):
            argnames = argnames[1:]
        fname = "key_" + func.__name__
        code = 'def %s(%s): return "%s" %% (%s)\ndel defaults' % (
            fname,
            ", ".join(args),
            key_format(func, key_prefix),
            ", ".join(argnames),
        )
        return compile_source(code, "keys_" + key_prefix, defaults)[fname]

    return build


# region: internal details


def compile_source(source, name, defaults):
    compiled = compile(source, name, "exec")
    local_vars = {"defaults": defaults}
    exec(compiled, {}, local_vars)
    return local_vars
