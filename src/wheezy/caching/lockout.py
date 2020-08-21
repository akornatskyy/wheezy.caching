""" ``lockout`` module.
"""

from warnings import warn

from wheezy.caching.utils import total_seconds


class Locker(object):
    """Used to define lockout terms."""

    def __init__(
        self, cache, forbid_action, namespace=None, key_prefix="c", **terms
    ):
        self.cache = cache
        self.forbid_action = forbid_action
        self.namespace = namespace
        self.key_prefix = key_prefix
        self.terms = terms

    def define(self, name, **terms):
        """Defines a new lockout with given `name` and `terms`.
        The `terms` keys must correspond to `known terms` of locker.
        """
        if not terms:  # pragma: nocover
            warn("Locker: no terms", stacklevel=2)
        key_prefix = "%s:%s:" % (self.key_prefix, name.replace(" ", "_"))
        counters = [self.terms[t](**terms[t]) for t in terms]
        return Lockout(
            name,
            counters,
            self.forbid_action,
            self.cache,
            self.namespace,
            key_prefix,
        )


class NullLocker(object):
    """Null locker implementation."""

    def __init__(
        self, cache, forbid_action, namespace=None, key_prefix="c", **terms
    ):
        pass

    def define(self, name, **terms):
        if not terms:  # pragma: nocover
            warn("NullLocker: no terms", stacklevel=2)
        return NullLockout()


class Counter(object):
    """A container of various attributes used by lockout."""

    def __init__(
        self, key_func, count, period, duration, reset=True, alert=None
    ):
        self.key_func = key_func
        self.count = count
        self.period = total_seconds(period)
        self.duration = total_seconds(duration)
        self.reset = reset
        self.alert = alert


class Lockout(object):
    """A lockout is used to enforce terms of use policy."""

    def __init__(
        self, name, counters, forbid_action, cache, namespace, key_prefix
    ):
        self.name = name
        self.counters = counters
        self.cache = cache
        self.namespace = namespace
        self.key_prefix = key_prefix
        self.forbid_action = forbid_action

    def guard(self, func):
        """A guard decorator is applied to a `func` which returns a
        boolean indicating success or failure. Each failure is a
        subject to increase counter. The counters that support
        `reset` (and related locks) are deleted on success.
        """

        def guard_wrapper(ctx, *args, **kwargs):
            succeed = func(ctx, *args, **kwargs)
            if succeed:
                self.reset(ctx)
            else:
                self.incr(ctx)
            return succeed

        return guard_wrapper

    def quota(self, func):
        """A quota decorator is applied to a `func` which returns a
        boolean indicating success or failure. Each success is a
        subject to increase counter.
        """

        def quota_wrapper(ctx, *args, **kwargs):
            succeed = func(ctx, *args, **kwargs)
            if succeed:
                self.incr(ctx)
            return succeed

        return quota_wrapper

    def forbid_locked(self, wrapped=None, action=None):
        """A decorator that forbids access (by a call to `forbid_action`)
        to `func` once the counter threshold is reached (lock is set).

        You can override default forbid action by `action`.

        See `test_lockout.py` for an example.
        """
        action = action or self.forbid_action
        assert action

        def decorate(func):
            key_prefix = "lock:" + self.key_prefix

            def forbid_locked_wrapper(ctx, *args, **kwargs):
                locks = self.cache.get_multi(
                    [key_prefix + c.key_func(ctx) for c in self.counters],
                    self.namespace,
                )
                if locks:
                    return action(ctx)
                return func(ctx, *args, **kwargs)

            return forbid_locked_wrapper

        if wrapped is None:
            return decorate
        else:
            return decorate(wrapped)

    def reset(self, ctx):
        """Removes locks for counters that support reset."""
        key_prefix = self.key_prefix
        keys = [key_prefix + c.key_func(ctx) for c in self.counters if c.reset]
        keys.extend(["lock:" + key for key in keys])
        keys and self.cache.delete_multi(keys, 0, self.namespace)

    def force_reset(self, ctx):
        """Removes locks for all counters."""
        key_prefix = self.key_prefix
        keys = [key_prefix + c.key_func(ctx) for c in self.counters]
        keys.extend(["lock:" + key for key in keys])
        keys and self.cache.delete_multi(keys, 0, self.namespace)

    def incr(self, ctx):
        """Increments lockout counters for given context."""
        key_prefix = self.key_prefix
        for c in self.counters:
            key = key_prefix + c.key_func(ctx)
            max_try = (
                self.cache.add(key, 1, c.period, self.namespace)
                and 1
                or self.cache.incr(key, 1, self.namespace)
            )
            # print("%s ~ %d" % (key, max_try))
            if max_try >= c.count:
                self.cache.delete(key, 0, self.namespace)
                self.cache.add("lock:" + key, 1, c.duration, self.namespace)
                c.alert and c.alert(ctx, self.name, c)


class NullLockout(object):
    """Null lockout implementation."""

    def guard(self, func):
        return func

    def quota(self, func):
        return func

    def forbid_locked(self, wrapped=None, action=None):
        def decorate(func):
            return func

        if wrapped is None:
            return decorate
        else:
            return wrapped

    def reset(self, ctx):
        pass

    def force_reset(self, ctx):
        pass

    def incr(self, ctx):
        pass
