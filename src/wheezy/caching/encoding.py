
""" ``encoding`` module.
"""

from wheezy.caching.comp import string_type


def encode_keys(mapping, key_encode):
    """ Encodes all keys in mapping with ``key_encode`` callable.
        Returns tuple of: key mapping (encoded key => key) and
        value mapping (encoded key => value).
    """
    key_mapping = {}
    encoded_mapping = {}
    for key in mapping:
        encoded_key = key_encode(key)
        key_mapping[encoded_key] = key
        encoded_mapping[encoded_key] = mapping[key]
    return key_mapping, encoded_mapping


def string_encode(key):
    """ Encodes ``key`` with UTF-8 encoding.
    """
    if key and isinstance(key, string_type):
        return key.encode('UTF-8')
    else:
        return key
