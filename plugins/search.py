#!/usr/bin/env python
#-*- coding: utf-8 -*-


import json
import urllib2
from urllib import quote


google_url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=%s'


def google(api, matches, origin, dest, text):

    if dest.startswith('#'):
        send_to = dest
    else:
        send_to = origin['nick']

    query = matches.group(1)
    if not query:
        api.msg(send_to, 'No search query given...')

    res = urllib2.urlopen(google_url % quote(query.encode('utf-8')))
    data = json.load(res)
    res.close()

    if len(data['responseData']['results']) > 0:
        api.msg(send_to, '%s: %s' % (
            data['responseData']['results'][0]['titleNoFormatting'],
            data['responseData']['results'][0]['unescapedUrl']
        ))
    else:
        api.msg(send_to, 'No results...')

google.events = ('receive-msg', 'receive-privmsg')
google.regex = ('text', '^\$g(?:oogle)? (.*?)$')
google.thread = True
