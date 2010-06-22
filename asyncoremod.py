"""
A small modification of asyncore. Refer to the asyncore module for the license.
"""


import select
import asyncore


# This function is identical to the poll2 function in asyncore, except that it
# uses selectepoll instead of select.poll
def epoll(timeout=0.0, map=None):
    # Use the epoll() support added to the select module in Python 2.6

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


if hasattr(select, 'epoll'):
    _poll = epoll
elif hasattr(select, 'poll'):
    _poll = asyncore.poll2
else:
    _poll = asyncore.poll


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
