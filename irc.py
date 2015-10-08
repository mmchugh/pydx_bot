import json
import socket
import threading
import time


class PyBot(object):
    def __init__(self, host, name):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, 6667))

        self.socket.send("USER {0} 0 * :{0}\n".format(name))
        self.socket.send("NICK {}\n".format(name))

        self.listen_thread = threading.Thread(target=self._listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        self.irc_handlers = {
            'PING': self.pong,
            'PRIVMSG': self.privmsg,
        }

    def join_channel(self, channel):
        self.socket.send("JOIN :{}\n".format(channel))

    def message(self, recipient, message):
        self.socket.send("PRIVMSG {} :{}\n".format(recipient, message))

    def pong(self, source, message):
        self.socket.send("PONG :{}\n".format(message[1:]))

    def privmsg(self, source, arg_string):
        destination, message = arg_string.split(' :')
        if message.startswith('!'):
            print 'command {} from {}'.format(message[1:], source)

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

    def _listen(self):
        while True:
            message = self.socket.recv(1024)
            self.parse_message(message.strip())

config = json.load(open('bot.json'))

host = config.get('host', 'localhost')
name = config.get('name', 'pybot')
channel = config.get('channel', '#pydx')

questions_path = config.get('questions_path', 'questions.txt')
answers_path = config.get('answers_path', 'answers.txt')

questions = [line.strip() for line in open(questions_path)]
answers = [line.strip() for line in open(answers_path)]

bot = PyBot(host, name)

bot.join_channel(channel)
bot.message(channel, 'Hello!')
bot.message(channel, 'To start a game, type "!start"')
bot.message(channel, 'I have {} questions with {} answers'.format(
    len(questions), len(answers)
))

while True:
    time.sleep(1)
