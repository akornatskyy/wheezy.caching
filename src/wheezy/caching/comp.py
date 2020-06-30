""" ``comp`` module.
"""

import sys

PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3


if PY3:  # pragma: nocover

    def iteritems(d):
        return d.items()

    def itervalues(d):
        return d.values()

    xrange = range
    string_type = str

    def list_map(f, iter):
        return list(map(f, iter))


else:  # pragma: nocover

    def iteritems(d):
        return d.iteritems()  # noqa: B301

    def itervalues(d):
        return d.itervalues()  # noqa: B301

    xrange = xrange
    string_type = unicode  # noqa: F821

    list_map = map


if PY3:  # pragma: nocover
    from _thread import allocate_lock
else:  # pragma: nocover
    from thread import allocate_lock  # noqa

if PY2 and PY_MINOR == 4:  # pragma: nocover
    __import__ = __import__
else:  # pragma: nocover
    # perform absolute import
    __saved_import__ = __import__

    def __import__(name, globals=None, locals=None, f=None):  # noqa: N807
        return __saved_import__(name, globals, locals, f, 0)


if PY3:  # pragma: nocover
    from queue import Queue
else:  # pragma: nocover
    from Queue import Queue  # noqa
