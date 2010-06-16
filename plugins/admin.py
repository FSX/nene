#!/usr/bin/env python
#-*- coding: utf-8 -*-


def join(api, matches, origin, dest, text):
    api.join(matches.group(1))


def part(api, matches, origin, dest, text):
    api.part(matches.group(1))


def quit(api, matches, origin, dest, text):
    api.quit(matches.group(1))


config = [
    {
        'function': join,
        'regex': ['text', '^\$join (#\S+)$'],
        'event': 'receive-privmsg'
    },
    {
        'function': part,
        'regex': ['text', '^\$part (#\S+)$'],
        'event': 'receive-privmsg'
    },
    {
        'function': quit,
        'regex': ['text', '^\$quit(?: (.*))?$'],
        'event': 'receive-privmsg'
    }
]
