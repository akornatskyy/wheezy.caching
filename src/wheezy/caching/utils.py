""" ``utils`` module.
"""

from datetime import timedelta


def total_seconds(delta):
    """Returns a total number of seconds for the given delta.

    ``delta`` can be ``datetime.timedelta``.

    >>> total_seconds(timedelta(hours=2))
    7200

    or int:

    >>> total_seconds(100)
    100

    otherwise raise ``TypeError``.

    >>> total_seconds('100') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    if isinstance(delta, int):
        return delta
    elif isinstance(delta, timedelta):
        return delta.seconds + delta.days * 86400
    else:
        raise TypeError(
            "Expecting type datetime.timedelta " "or int for seconds"
        )
