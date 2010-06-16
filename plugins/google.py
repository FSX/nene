#!/usr/bin/env python
#-*- coding: utf-8 -*-


import json
import urllib


def google_plugin(api, matches, origin, dest, text):

    query = matches.group(1)
    uri = 'http://ajax.googleapis.com/ajax/services/search/web'
    args = '?v=1.0&safe=off&q=' + urllib.quote(query.encode('utf-8'))
    res = urllib.urlopen(uri + args)
    data = json.load(res)

    if len(data['responseData']['results']) > 0:
        api.msg(dest, '%s: %s' % (
            data['responseData']['results'][0]['titleNoFormatting'],
            data['responseData']['results'][0]['unescapedUrl']
        ))
    else:
        api.msg(dest, 'No results...')


config = [
    {
        'function': google_plugin,
        'regex': ['text', '^\$g(?:oogle)? (.*?)$'],
        'event': 'receive-msg',
        'thread': True
    }
]
