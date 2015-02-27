
""" Unit tests for ``wheezy.caching.lockout``.
"""

import unittest

from datetime import timedelta

from wheezy.caching.memory import MemoryCache
from wheezy.caching.lockout import Counter
from wheezy.caching.lockout import Locker


# region: alerts

alerts = []


def send_mail(s, name, counter):
    assert isinstance(s, MyService)
    alerts.append('send mail: %s' % name)


def send_sms(s, name, counter):
    assert isinstance(s, MyService)
    alerts.append('send sms: %s' % name)


def ignore_alert(s, name, counter):
    assert isinstance(s, MyService)
    alerts.append('ignore: %s' % name)


# region: lockouts and defaults

def lockout_by_id(count=10,
                  period=timedelta(minutes=1),
                  duration=timedelta(hours=2),
                  reset=False,
                  alert=send_mail):

    def key_func(s):
        return 'by_id:%s' % s.user_id
    return Counter(key_func=key_func, count=count,
                   period=period, duration=duration,
                   reset=reset, alert=alert)


def lockout_by_ip(count=10,
                  period=timedelta(minutes=1),
                  duration=timedelta(hours=2),
                  reset=True,
                  alert=send_sms):

    def key_func(s):
        return 'by_ip:%s' % s.user_ip
    return Counter(key_func=key_func, count=count,
                   period=period, duration=duration,
                   reset=reset, alert=alert)


def lockout_by_id_ip(count=10,
                     period=timedelta(minutes=1),
                     duration=timedelta(hours=2),
                     reset=True,
                     alert=ignore_alert):

    def key_func(s):
        return 'by_id_ip:%s:%s' % (s.user_id, s.user_ip)
    return Counter(key_func=key_func, count=count,
                   period=period, duration=duration,
                   reset=reset, alert=alert)


# region: config

cache = MemoryCache()
locker = Locker(cache, key_prefix='my_app',
                forbid_action=lambda s: 'forbidden',
                by_id=lockout_by_id,
                by_ip=lockout_by_ip,
                by_id_ip=lockout_by_id_ip)


# region: service/handler

class MyService(object):

    lockout = locker.define(
        name='action',
        by_id_ip=dict(count=4, duration=60),
        by_id=dict(count=6, duration=timedelta(minutes=2)),
        by_ip=dict(count=8, duration=timedelta(minutes=5))
    )

    lockout2 = locker.define(
        name='action 2',
        by_ip=dict(count=4, duration=timedelta(minutes=5), reset=False)
    )

    action_result = False
    user_id = None
    user_ip = None

    @lockout.forbid_locked
    def action(self):
        if self.do_action():
            return 'show ok'
        else:
            return 'show error'

    @lockout.forbid_locked(action=lambda s: 'show captcha')
    def action2(self):
        if self.do_action():
            return 'show ok'
        else:
            return 'show error'

    @lockout.guard
    def do_action(self):
        return self.action_result

    @lockout.forbid_locked
    def action3(self):
        if self.do_action3():
            return 'show ok'
        else:
            return 'show error'

    @lockout.quota
    def do_action3(self):
        return self.action_result

    @lockout2.forbid_locked
    def action4(self):
        if self.do_action4():
            return 'show ok'
        else:
            return 'show error'

    @lockout2.guard
    def do_action4(self):
        return self.action_result


# region: test case

class LockoutTestCase(unittest.TestCase):

    def setUp(self):
        del alerts[:]
        cache.flush_all()

    def test_forbidden(self):
        s = MyService()
        s.user_id = 'u1'
        s.user_ip = 'ip1'
        for i in range(4):
            assert 'show error' == s.action()
        assert ['ignore: action'] == alerts
        del alerts[:]
        assert 'forbidden' == s.action(), 'lock by id/ip'

        s.user_ip = 'ip2'
        for i in range(2):
            assert 'show error' == s.action()
        assert ['send mail: action'] == alerts
        del alerts[:]
        assert 'forbidden' == s.action(), 'lock by id'

        s.user_id = 'u3'
        for i in range(3):
            assert 'show error' == s.action()
        s.user_id = 'u4'
        for i in range(3):
            assert 'show error' == s.action()
        assert ['send sms: action'] == alerts
        assert 'forbidden' == s.action(), 'lock by ip'

    def test_reset_on_success(self):
        s = MyService()
        s.user_id = 'u0'
        s.user_ip = 'ip0'
        for i in range(2):
            assert 'show error' == s.action()

        s.action_result = True
        assert 'show ok' == s.action()

        s.action_result = False
        for i in range(4):
            assert 'show error' == s.action()
        assert 'forbidden' == s.action()

    def test_reset(self):
        s = MyService()
        s.user_id = 'u0'
        s.user_ip = 'ip0'
        # reset supported
        for i in range(4):
            assert 'show error' == s.action()
        assert 'forbidden' == s.action()
        s.lockout.reset(s)
        assert 'show error' == s.action()
        # reset not supported
        for i in range(4):
            s.action4()
        assert 'forbidden' == s.action4()
        s.lockout2.reset(s)
        assert 'forbidden' == s.action4()

    def test_force_reset(self):
        s = MyService()
        s.user_id = 'u0'
        s.user_ip = 'ip0'
        # reset supported
        for i in range(4):
            assert 'show error' == s.action()
        assert 'forbidden' == s.action()
        s.lockout.force_reset(s)
        assert 'show error' == s.action()
        # reset not supported
        for i in range(4):
            s.action4()
        assert 'forbidden' == s.action4()
        s.lockout2.force_reset(s)
        assert 'show error' == s.action4()

    def test_custom_forbid_action(self):
        s = MyService()
        s.user_id = 'cfa-u1'
        s.user_ip = 'cfa-ip1'
        for i in range(4):
            assert 'show error' == s.action2()
        assert 'show captcha' == s.action2()

    def test_quota(self):
        s = MyService()
        s.user_id = 'u1q'
        s.user_ip = 'ip1q'
        for i in range(10):
            assert 'show error' == s.action3()
        assert [] == alerts
        del alerts[:]

        s.action_result = True
        for i in range(4):
            assert 'show ok' == s.action3()
        assert ['ignore: action'] == alerts
        assert 'forbidden' == s.action3(), 'lock by id/ip'


class NullLockoutTestCase(unittest.TestCase):

    def test_locker(self):
        from wheezy.caching.lockout import NullLocker
        from wheezy.caching.lockout import NullLockout
        locker = NullLocker(cache, key_prefix='my_app',
                            forbid_action=lambda s: 'forbidden',
                            by_id=lockout_by_id,
                            by_ip=lockout_by_ip,
                            by_id_ip=lockout_by_id_ip)
        assert isinstance(locker.define('x', by_id_ip={}), NullLockout)

    def test_lockout(self):
        from wheezy.caching.lockout import NullLockout
        l = NullLockout()

        def f():
            pass
        assert f == l.guard(f)
        assert f == l.quota(f)
        assert f == l.forbid_locked(f)
        assert f == l.forbid_locked(action=None)(f)
        l.reset(None)
        l.force_reset(None)
        l.incr(None)
