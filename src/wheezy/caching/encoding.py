""" ``encoding`` module.
"""

from base64 import b64encode

BASE64_ALTCHARS = "-_".encode("latin1")


def encode_keys(mapping, key_encode):
    """Encodes all keys in mapping with ``key_encode`` callable.
    Returns tuple of: key mapping (encoded key => key) and
    value mapping (encoded key => value).

    >>> mapping = {'k1': 1, 'k2': 2}
    >>> keys, mapping = encode_keys(mapping,
    ...         lambda k: str(base64_encode(k).decode('latin1')))
    >>> sorted(keys.items())
    [('azE=', 'k1'), ('azI=', 'k2')]
    >>> sorted(mapping.items())
    [('azE=', 1), ('azI=', 2)]
    """
    key_mapping = {}
    encoded_mapping = {}
    for key in mapping:
        encoded_key = key_encode(key)
        key_mapping[encoded_key] = key
        encoded_mapping[encoded_key] = mapping[key]
    return key_mapping, encoded_mapping


def string_encode(key):
    """Encodes ``key`` with UTF-8 encoding."""
    if isinstance(key, str):
        return key.encode("UTF-8")
    else:
        return key  # pragma: nocover


def base64_encode(key):
    """Encodes ``key`` with base64 encoding.

    >>> result = base64_encode('my key')
    >>> result == 'bXkga2V5'.encode('latin1')
    True
    """
    if isinstance(key, str):
        key = key.encode("UTF-8")
    return b64encode(key, BASE64_ALTCHARS)


def hash_encode(hash_factory):
    """Encodes ``key`` with given hash function.

    See list of available hashes in ``hashlib``
    module from Python Statndard Library.

    Additional algorithms may also be available
    depending upon the OpenSSL library that Python
    uses on your platform.

    >>> try:
    ...     from hashlib import sha1
    ...     key_encode = hash_encode(sha1)
    ...     r = base64_encode(key_encode('my key'))
    ...     assert r == 'RigVwkWdSuGyFu7au08PzUMloU8='.encode('latin1')
    ... except ImportError:  # Python2.4
    ...     pass
    """
    assert callable(hash_factory)

    def key_encode(key):
        h = hash_factory()
        if isinstance(key, str):
            key = key.encode("UTF-8")
        h.update(key)
        return h.digest()

    return key_encode
