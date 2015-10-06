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

    def _listen(self):
        while True:
            message = self.socket.recv(1024)
            print message


bot = PyBot('localhost', 'bot')

bot.join_channel('#pydx')
bot.message('#pydx', 'Hello!')

time.sleep(10)

bot.message('#pydx', 'All right, bye!')
