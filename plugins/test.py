#!/usr/bin/env python
#-*- coding: utf-8 -*-


def test_plugin(api, matches, origin, dest, text):
    api.msg(dest, 'This is a test!')


config = [
    {
        'function': test_plugin,
        'regex': {
            'subject': 'text',
            'pattern': '^\$test$'
        },
        'event': 'recieve-msg'
    }
]
