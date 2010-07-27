#!/usr/bin/env python
#-*- coding: utf-8 -*-


import os
import os.path
import aiml


aaa_files = '/home/frank/Projects/Nene/data/aaa-aiml'
kernel = aiml.Kernel()


for fn in os.listdir(aaa_files):
    if fn.endswith('.aiml'):
        kernel.learn(os.path.join(aaa_files, fn))


def respond(api, matches, origin, dest, text):

    global kernel

    try:
        response = kernel.respond(matches.group(1), origin['nick'])
        if response:
            api.msg(dest, '%s: %s' % (origin['nick'], response))
    except Exception as e:
        print e

respond.events = ('receive-msg',)
respond.regex = ('text', '^Nene: (.*)$')
