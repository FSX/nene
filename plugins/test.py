#!/usr/bin/env python
#-*- coding: utf-8 -*-


def test_plugin(api, matches, origin, dest, text):
    api.msg(dest, 'This is a test!')


config = [
    {
        'function': test_plugin,
        'regex': ['text', '^\$test$'],
        'event': 'receive-msg'
    }
]
