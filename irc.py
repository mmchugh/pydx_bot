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

    def join_channel(self, channel):
        self.socket.send("JOIN :{}\n".format(channel))

    def message(self, recipient, message):
        self.socket.send("PRIVMSG {} :{}\n".format(recipient, message))

    def pong(self, message):
        self.socket.send("PONG :{}\n".format(message))

    def parse_message(self, message):
        if message.startswith(':'):
            source, command_message = message[1:].split(' ', 1)
            user = source.split('!')[0]
        else:
            user, command_message = None, message

        command, args = command_message.split(' ', 1)

        print 'Command {} from {} with args ({})'.format(command, user, args)

    def _listen(self):
        while True:
            message = self.socket.recv(1024)
            self.parse_message(message.strip())


bot = PyBot('localhost', 'bot')

bot.join_channel('#pydx')
bot.message('#pydx', 'Hello!')

while True:
    time.sleep(1)
