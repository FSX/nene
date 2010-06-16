#!/usr/bin/env python
#-*- coding: utf-8 -*-


def test(api, matches, origin, dest, text):
    api.msg(dest, 'This is a test!')


config = [
    {
        'function': test,
        'regex': ['text', '^\$test$'],
        'event': 'receive-msg'
    }
]
