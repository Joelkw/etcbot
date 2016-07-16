
import sys
import socket
import uuid

from twisted.internet import reactor, protocol as p

TEAMNAME = 'IMMEDEBUG'
EXCHANGE_URL = 'test-exch-teamname'
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
        print 'hi', self.factory.data
        self._id = 0
        self.SendHello()
    
    def dataReceived(self, data):
        print 'Received', data

    def Send(self, arg):
        self.transport.write(arg)
  
    def SendHello(self):
        return self.Send('HELLO ' + TEAMNAME)

    def GetUUID(self):
        self._id += 1
        return self._id
    
    def _SendOrder(self, ty, sym, buy, price, size):
        uuid = self.GetUUID()
        return self.Send(
                '{0} {1} {2} {3} {4} {5} {6}'.format(
                    ty, uuid, sym, buy, price, size))

    def SendOrder(self, *args, **kwargs):
        ret = self._SendOrder(*args, **kwargs)
        if 'ACK' in ret:
            return True, None
        else:
            return False, ret

    def SendBondOrder(self):

        for i in range(50):
            price = 950
            self.SendOrder('ADD', 'BOND', 'BUY', price + i, 100)

        for i in range(50):
            price = 1001
            self.SendOrder('ADD', 'BOND', 'SELL', price + i, 100)

class BaseBotFactory(p.ClientFactory):

    protocol = BaseBotClient

    def __init__(self):
        pass

reactor.connectTCP(EXCHANGE_URL, 20000, BaseBotFactory())
reactor.run()
