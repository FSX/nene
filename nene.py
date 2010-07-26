"""
Nene, An IRC-bot.
Copyright 2010, Frank Smit, 61924.nl
Licensed under the Eiffel Forum License 2.

Nene is a simple IRC-bot. It's just a project for fun to improve my knowledge
of Python. I'm using Phenny as a reference and I'm also using some code from
Phenny. And I'll probably also port some plugins. Therefore this project is
licensed under the Eiffel Forum License 2. That's the same license Phenny's
using.

 [Phenny]: http://inamidst.com/phenny/

"""


import os
import re
import sys
import imp
import socket
import asyncoremod
import asynchat
from thread import start_new_thread
from ConfigParser import SafeConfigParser


DEFAULT_PORT = 6667
PLUGIN_PATH = 'plugins'
RE_ORIGIN = re.compile(r'([^!]*)!?([^@]*)@?(.*)')


def safe_input(input):
    input = input.replace('\n', '')
    input = input.replace('\r', '')
    return input.encode('utf-8')


def parse_origin(raw_origin):
    """Parse a string similar to 'FSX!~FSX@241b33b.3cae4b8e.direct-adsl.nl'
    into 'FSX', '~FSX' and '241b33b.3cae4b8e.direct-adsl.nl'"""

    match = RE_ORIGIN.match(raw_origin or '')
    return match.groups() # Nickname, username, hostname


class Event(object):
    """A simple event class."""

    listeners = {}

    def __init__(self, verbose=False):
        self.verbose = verbose

    def register(self, event, func, regex, thread=False):
        """Register/Add a function to a event."""

        if event not in self.listeners:
            self.listeners[event] = set()
        self.listeners[event].add((func, regex, thread))

    def call(self, event, data=None):
        """Call all functions connected to the specified event."""

        def run_plugin(func, regex, data=None):
            if regex and regex[0] in data:
                data['matches'] = regex[1].match(data[regex[0]])
                if not data['matches']:
                    return
            if data is None:
                func()
            else:
                if type(data) == type([]):
                    func(*data)
                elif type(data) == type({}):
                    func(**data)
                else:
                    func(data)

        if event in self.listeners:
            if self.verbose:
                print '\x1b[33m++\x1b[0m  Event: %s - running %d plugin function(s)' % \
                    (event, len(self.listeners[event]))
            for func, regex, thread in self.listeners[event]:
                if thread:
                    start_new_thread(run_plugin, (func, regex, data))
                else:
                    run_plugin(func, regex, data)


class API(object):
    """This is the plublic API for plugins."""

    def __init__(self, irc, cfg):
        self.__irc = irc
        self.cfg = cfg

    def join(self, channel):
        self.__irc._write(('JOIN',), channel)

    def part(self, channel, text=None):
        self.__irc._write(('PART', channel), text)

    def msg(self, recipient, text):
        self.__irc._write(('PRIVMSG', recipient), text)

    def notice(self, recipient, text):
        self.__irc._write(('NOTICE', recipient), text)

    def quit(self, text=None):
        self.__irc._write(('QUIT',), text)


class IRCBot(asynchat.async_chat):
    """A simple IRC bot that connects to the host and launches an 'event' when
    data is recieved and send."""

    def __init__(self, cfg, nick, name, channels, password=None, plugin_path=None):
        asynchat.async_chat.__init__(self)

        self.buffer = []
        self.verbose = cfg.getboolean('irc', 'verbose')
        self.set_terminator('\n')
        self.event = Event(self.verbose)
        self.api = API(self, cfg)

        self.nick = nick
        self.user = nick
        self.name = name
        self.channels = channels or []
        self.password = password

        if os.path.exists(plugin_path):
            self._find_plugins(plugin_path)

    def _find_plugins(self, plugin_path):
        """Find all the plugins and load them."""

        for fn in os.listdir(plugin_path):
            if fn.endswith('.py') and not fn.startswith('_'):
                self._load_plugin(os.path.join(plugin_path, fn))

    def _load_plugin(self, file_path):
        """Load a plugin and bind the plugin functions to events."""

        name = os.path.basename(file_path)[:-3]
        plugin = imp.load_source(name, file_path)

        for func in plugin.__dict__.values():
            if hasattr(func, 'events'):
                if hasattr(func, 'regex'):
                    func.regex = (func.regex[0], re.compile(func.regex[1]))
                else:
                    func.regex = ()
                if not hasattr(func, 'thread'):
                    func.thread = False
                for event in func.events:
                    self.event.register(event, func, func.regex, func.thread)

        if self.verbose:
            print '\x1b[31m--\x1b[0m  Loaded plugin: %s ' % name

    def _write(self, args, text=None):
        """Write a message to the server."""

        if text is not None:
            if self.verbose:
                print '\x1b[32m>>\x1b[0m  %s :%s' % (' '.join(args), safe_input(text))
            self.push('%s :%s\r\n' % (' '.join(args), safe_input(text)))
        else:
            if self.verbose:
                print '\x1b[32m>>\x1b[0m  %s' % ' '.join(args)
            self.push('%s\r\n' % ' '.join(args))

    def handle_connect(self):
        """Called when the socket connects."""

        if self.verbose:
            print '\x1b[31m--\x1b[0m  Connected to IRC-server!'

        if self.password:
            self._write(('PASS', self.password))

        self._write(('NICK', self.nick))
        self._write(('USER', self.user, '+iw', self.nick), self.name)

        for channel in self.channels:
            self._write(('JOIN',), channel)

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        """Process data that comes from the server."""

        line = ''.join(self.buffer)
        if line.endswith('\r'):
            line = line[:-1]
        self.buffer = []

        if self.verbose:
            print '\x1b[34m<<\x1b[0m  %s' % line

        if line.startswith(':'):
            source, line = line[1:].split(' ', 1)
        else:
            source = None

        if ' :' in line:
            argstr, text = line.split(' :', 1)
        else:
            argstr, text = line, ''
        args = argstr.split()

        # Parse the source (where the data comes from)
        nickname, username, hostname = parse_origin(source)

        # Respond to server ping to keep connection alive
        if args[0] == 'PING':
            self._write(('PONG', text))

        # Prepare event arguments and call the event
        if args[0] in ('PING', 'JOIN', 'PART', 'PRIVMSG', 'NOTICE'):

            event_args = {'api': self.api, 'matches': None}
            text = text.strip()

            if args[0] == 'PING':
                event_args['server'] = text
            else:
                event_args['origin'] = {
                    'nick': nickname,
                    'user': username,
                    'host': hostname
                }

                if args[0] == 'JOIN':
                    event_args['channel'] = text
                elif args[0] == 'PART':
                    event_args['channel'] = args[1]
                else:
                    event_args['dest'] = args[1]
                    event_args['text'] = text

                # If the destination is a channel then it's just a normal message
                if args[0] == 'PRIVMSG' and args[1].startswith('#'):
                    args[0] = 'MSG'

            self.event.call('receive-' + args[0].lower(), event_args)

    def run(self, host, port=DEFAULT_PORT):
        """Run the IRC bot (connect to the host)."""

        if self.verbose:
            print '\x1b[31m--\x1b[0m  Connecting to %s:%s...' % (host, port)

        try:
            self.event.call('pre-connect', {'api': self.api})
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((host, port))
            asyncoremod.loop()
        except KeyboardInterrupt:
            self._write(('QUIT',)) # Properly quit the IRC server
            self.event.call('post-disconnect', {'api': self.api})
            sys.exit()


if __name__ == '__main__':

    try:
        config_file = sys.argv[1]
    except:
        print >> sys.stderr, 'Missing configuration file!'
        sys.exit()

    cp = SafeConfigParser()
    cp.read(config_file)

    ircbot = IRCBot(**{
        'cfg': cp,
        'nick': cp.get('bot', 'nick'),
        'name': cp.get('bot', 'name'),
        'channels': cp.get('bot', 'channels').split(', '),
        'password': cp.get('bot', 'password'),
        'plugin_path': cp.get('plugins', 'path')
    })

    ircbot.run(cp.get('irc', 'host'), cp.getint('irc', 'port'))
