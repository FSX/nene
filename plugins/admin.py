#!/usr/bin/env python
#-*- coding: utf-8 -*-


def join(api, matches, origin, dest, text):
    api.join(matches.group(1))

join.events = ('receive-privmsg',)
join.regex = ('text', '^\$join (#\S+)$')


def part(api, matches, origin, dest, text):
    api.part(matches.group(1))

part.events = ('receive-privmsg',)
part.regex = ('text', '^\$part (#\S+)$')


def quit(api, matches, origin, dest, text):
    api.quit(matches.group(1))

quit.events = ('receive-privmsg',)
quit.regex = ('text', '^\$quit(?: (.*))?$')
