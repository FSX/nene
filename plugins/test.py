#!/usr/bin/env python
#-*- coding: utf-8 -*-


def test(api, matches, origin, dest, text):
    api.msg(dest, 'This is a test!')

test.events = ('receive-msg',)
test.regex = ('text', '^\$test$')
