
""" ``comp`` module.
"""

import sys


PY3 = sys.version_info[0] >= 3

if PY3:  # pragma: nocover
    iteritems = lambda d: d.items()
    itervalues = lambda d: d.values()
    xrange = range
else:  # pragma: nocover
    iteritems = lambda d: d.iteritems()
    itervalues = lambda d: d.itervalues()
    xrange = xrange


if PY3:  # pragma: nocover
    from _thread import allocate_lock
else:  # pragma: nocover
    from thread import allocate_lock
