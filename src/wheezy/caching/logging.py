""" `logging` module.
"""

from hashlib import sha1
from logging import Handler

from wheezy.caching.encoding import hash_encode
from wheezy.caching.utils import total_seconds


class OnePassHandler(Handler):
    """One pass logging handler is used to proxy a message to inner
    handler once per one pass duration.
    """

    def __init__(self, inner, cache, time, key_encode=None, namespace=None):
        """Initialize the instance with the inner logging handler,
        cache to use, time to keep lock, key encode and namespace.
        """
        super(OnePassHandler, self).__init__()
        self.inner = inner
        self.cache = cache
        self.time = total_seconds(time)
        self.key_encode = key_encode or hash_encode(sha1)
        self.namespace = namespace

    def emit(self, record):
        """Emit a record. Use log record message as a key in cache."""
        key = self.key_encode(record.getMessage())
        if self.cache.add(key, record.created, self.time, self.namespace):
            self.inner.emit(record)
