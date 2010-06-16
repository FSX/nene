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
        'regex': {
            'subject': 'text',
            'pattern': '^\$join (#\S+)$'
        },
        'event': 'recieve-privmsg'
    },
    {
        'function': part,
        'regex': {
            'subject': 'text',
            'pattern': '^\$part (#\S+)$'
        },
        'event': 'recieve-privmsg'
    },
    {
        'function': quit,
        'regex': {
            'subject': 'text',
            'pattern': '^\$quit(?: (.*))?$'
        },
        'event': 'recieve-privmsg'
    }
]
