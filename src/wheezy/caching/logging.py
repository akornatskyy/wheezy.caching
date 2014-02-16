
""" `logging` module.
"""

from wheezy.caching.comp import __import__
from wheezy.caching.utils import total_seconds


Handler = __import__('logging', None, None, ['Handler']).Handler


class OnePassHandler(Handler):
    """ One pass logging handler is used to proxy a message to inner
        handler once per one pass duration.
    """

    def __init__(self, inner, cache, time, namespace=None):
        """ Initialize the instance with the inner logging handler,
            cache to use, time to keep lock and namespace.
        """
        super(OnePassHandler, self).__init__()
        self.inner = inner
        self.cache = cache
        self.time = total_seconds(time)
        self.namespace = namespace

    def emit(self, record):
        """ Emit a record. Use log record message as a key in cache.
        """
        key = record.getMessage()
        if self.cache.add(key, record.created, self.time, self.namespace):
            self.inner.emit(record)
