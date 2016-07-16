
import sys
import socket
import uuid
import threading


from twisted.internet import reactor, protocol as p

TEAMNAME = 'IMMEDEBUG'
# EXCHANGE_URL = 'test-exch-' + TEAMNAME.lower()
EXCHANGE_URL='production'
BUFFER = 1024

SYMBOLS = {
        'BOND': 'BOND',
        'VALBZ': 'VALBZ',
        'VALE': 'VALE',
        'GS': 'GS',
        'MS': 'MS',
        'WFC': 'WFC',
        'XLF': 'XLF'
        }

class BaseBotClient(p.Protocol):

    def connectionMade(self):
        print 'hi'
        self._id = 0
        self.SendHello()
	self.d = {}
	threading.Timer(1.0, self.sendbuyorders).start()
	threading.Timer(1.0, self.sendsellorders).start()
    
    def dataReceived(self, data):
	pass

    def Send(self, arg):
	print 'sending %s' % arg
        self.transport.write(arg + '\n')
  
    def SendHello(self):
        return self.Send('HELLO ' + TEAMNAME)

    def GetUUID(self):
        self._id += 1
        return self._id
    
    def _SendOrder(self, ty, sym, buy, price, size):
        uuid = self.GetUUID()
	self.d[uuid] = (buy, price, size)
        return self.Send(
                '{0} {1} {2} {3} {4} {5}'.format(
                    ty, uuid, sym, buy, price, size))

    def SendOrder(self, *args, **kwargs):
        self._SendOrder(*args, **kwargs)

    def SendBondOrder(self, buy, price, amount):
    	self.SendOrder('ADD', 'BOND', buy, price , amount)

    def sendbuyorders(self):
	price = 999
	for i in range(50):
		self.SendBondOrder('BUY', price, 1)

    def sendsellorders(self):
	price = 1001
	for i in range(50):
		self.SendBondOrder('SELL', price, 1)

class BaseBotFactory(p.ClientFactory):

    protocol = BaseBotClient

    def __init__(self):
        pass

reactor.connectTCP(EXCHANGE_URL, 20000, BaseBotFactory())
reactor.run()
