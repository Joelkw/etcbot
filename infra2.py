
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
    
    def dataReceived(self, datas):
      datas = datas.split('\n')
      for data in datas:
          data = data.split(' ')
          if data[0] == 'TRADE':
              sym = data[1]
              price = int(data[2])
              size = int(data[3])
              print sym, price
              if sym == 'BOND':
                self.sendbuyorders(price - 1, size)
                self.sendsellorders(price + 1, size)
                  

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

    def sendbuyorders(self, price, size):
	    self.SendBondOrder('BUY', price, size)

    def sendsellorders(self, price, size):
	    self.SendBondOrder('SELL', price, size)

class BaseBotFactory(p.ClientFactory):

    protocol = BaseBotClient

    def __init__(self):
        pass

reactor.connectTCP(EXCHANGE_URL, 20000, BaseBotFactory())
reactor.run()
