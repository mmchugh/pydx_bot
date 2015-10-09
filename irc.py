import json
import socket
import threading
import time


class PyBot(object):
    def __init__(self, config):
        self.host = config.get('host', 'localhost')
        self.name = config.get('name', 'pybot')
        self.channel = config.get('channel', '#pydx')

        self.questions_path = config.get('questions_path', 'questions.txt')
        self.answers_path = config.get('answers_path', 'answers.txt')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, 6667))

        self.socket.send("USER {0} 0 * :{0}\n".format(self.name))
        self.socket.send("NICK {}\n".format(self.name))

        self.listen_thread = threading.Thread(target=self._listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        self.irc_handlers = {
            'PING': self.pong,
            'PRIVMSG': self.privmsg,
        }

        self.game_handlers = {
            'start': self.start_game,
            'join': self.player_join,
            'play': self.player_answer,
            'choose': self.select_winner,
        }

        self.game_state = {}

        self.join_channel(self.channel)
        self.message(self.channel, 'Hello!')
        self.message(self.channel, 'To start a game, type "!start"')

    def join_channel(self, channel):
        self.socket.send("JOIN :{}\n".format(channel))

    def message(self, recipient, message):
        self.socket.send("PRIVMSG {} :{}\n".format(recipient, message))

    def pong(self, source, message):
        self.socket.send("PONG :{}\n".format(message[1:]))

    def privmsg(self, source, arg_string):
        destination, message = arg_string.split(' :')
        if message.startswith('!'):
            if ' ' in message:
                command, args = message[1:].split(' ', 1)
            else:
                command, args = message[1:], None
            if command in self.game_handlers:
                self.game_handlers[command](source, args)

    def parse_message(self, message):
        if message.startswith(':'):
            source, command_message = message[1:].split(' ', 1)
            user = source.split('!')[0]
        else:
            user, command_message = None, message

        command, args = command_message.split(' ', 1)

        print 'Command {} from {} with args ({})'.format(command, user, args)

        if command in self.irc_handlers:
            self.irc_handlers[command](user, args)

    def start_game(self, source, args):
        if self.game_state:
            self.player_join(source, None)
            return

        self.game_state = {
            'next_action': 'draw',
            'next_action_time': int(time.time()) + 30,
            'players': [],
            'questions': [line.strip() for line in open(self.questions_path)],
            'answers': [line.strip() for line in open(self.answers_path)],
        }

        self.message(self.channel, "Game started! First draw in 30 seconds.")
        self.player_join(source, '')

        self.tick()

    def player_join(self, source, args):
        if not self.game_state:
            self.start_game(source, None)
            return

        if source in [player['name'] for player in self.game_state['players']]:
            self.message(self.channel, '{} is already playing'.format(source))
            return

        player = {
            'name': source,
            'score': 0,
            'hand': [self._get_card() for _ in range(5)],
        }

        self.game_state['players'].append(player)

        self.message(self.channel, '{} has joined the game!'.format(source))

    def player_answer(self, source, args):
        pass

    def select_winner(self, source, args):
        pass

    def tick(self):
        pass

    def _get_card(self):
        pass

    def _listen(self):
        while True:
            message = self.socket.recv(1024)
            self.parse_message(message.strip())

config = json.load(open('bot.json'))

bot = PyBot(config)

while True:
    if bot.game_state:
        bot.tick()

    time.sleep(1)
