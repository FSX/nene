"""
A small modification of asyncore. Refer to the asyncore module for the license.
"""


import select
import asyncore


# This function is identical to the poll2 function in asyncore, except that it
# uses selectepoll instead of select.poll
def epoll_poller(timeout=0.0, map=None):
    """A poller which uses epoll(), supported on Linux 2.5.44 and newer."""

    if map is None:
        map = asyncore.socket_map
    if timeout is not None:
        # timeout is in milliseconds
        timeout = int(timeout*1000)
    pollster = select.epoll()
    if map:
        for fd, obj in map.items():
            flags = 0
            if obj.readable():
                flags |= select.POLLIN | select.POLLPRI
            if obj.writable():
                flags |= select.POLLOUT
            if flags:
                # Only check for exceptions if object was either readable
                # or writable.
                flags |= select.POLLERR | select.POLLHUP | select.POLLNVAL
                pollster.register(fd, flags)
        try:
            r = pollster.poll(timeout)
        except select.error, err:
            if err.args[0] != EINTR:
                raise
            r = []
        for fd, flags in r:
            obj = map.get(fd)
            if obj is None:
                continue
            asyncore.readwrite(obj, flags)


# From the patch at http://bugs.python.org/issue6692
def kqueue_poller(timeout=0.0, map=None):
    """A poller which uses kqueue(), BSD specific."""
    if map is None:
        map = socket_map
    if map:
        kqueue = select.kqueue()
        flags = select.KQ_EV_ADD | select.KQ_EV_ENABLE
        selectables = 0
        for fd, obj in map.items():
            filter = 0
            if obj.readable():
                filter |= select.KQ_FILTER_READ
            if obj.writable():
                filter |= select.KQ_FILTER_WRITE
            if filter:
                ev = select.kevent(fd, filter=filter, flags=flags)
                kqueue.control([ev], 0)
                selectables += 1

        events = kqueue.control(None, selectables, timeout)
        for event in events:
            fd = event.ident
            obj = map.get(fd)
            if obj is None:
                continue
            if event.filter == select.KQ_FILTER_READ:
                read(obj)
            if event.filter == select.KQ_FILTER_WRITE:
                write(obj)
        kqueue.close()


if hasattr(select, 'epoll'):
    _poll = epoll_poller         # Uses select.epoll
elif hasattr(select, 'kqueue'):
    _poll = kqueue_poller        # Uses select.kqueue
elif hasattr(select, 'poll'):
    _poll = asyncore.poll2       # Uses select.poll
else:
    _poll = asyncore.poll        # Uses select.select


# This is a slightly modified version of the loop function from asyncore
def loop(timeout=30.0, poller=_poll, map=None, count=None):
    if map is None:
        map = asyncore.socket_map

    if count is None:
        while map:
            poller(timeout, map)
    else:
        while map and count > 0:
            poller(timeout, map)
            count = count - 1
