
""" ``pools`` module.
"""

from Queue import Queue


class EagerPool(object):

    def __init__(self, create_factory, size):
        pool = Queue(size)
        for i in xrange(size):
            pool.put(create_factory())
        self.pool = pool
        self.acquire = pool.get
        self.get_back = pool.put


class Pooled(object):

    def __init__(self, pool):
        self.pool = pool

    def __enter__(self):
        self.item = item = self.pool.acquire()
        return item

    def __exit__(self, exc_type, exc_value, traceback):
        self.pool.get_back(self.item)
        self.item = None
