import sys
import socket
import uuid
import threading


from twisted.internet import reactor, protocol as p

TEAMNAME = 'IMMEDEBUG'
EXCHANGE_URL = 'test-exch-' + TEAMNAME.lower()
# EXCHANGE_URL='production'
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

class localBook(object):
  def __init__(self):
      localBook.symbols = ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]
      # let book be current price, stock:[(price, amount)] 
      # history is a list of historical averages
      localBook.book = {}
      for symbol in localBook.symbols:
          localBook.book[symbol] = {'lasttradeprice': 1000000, 'size': 0, 'totalorders': 0, 'oursells': [(0,0)], 'ourbuys':[(0,0)], 'sells': [(0,0)], 'buys': [(0,0)], 'avgbookbuy': 0, 'avgbooksell': 0, 'holding': 0, 'history': []}

  def trade_message(self, symbol, price):
      self.book[symbol]['lasttradeprice'] = price

  # orders are lists of tuples (price, size)
  def book_message(self, symbol, buyorders, sellorders):
      # because books update and we don't want duplicates just take 15 best
      self.book[symbol]['buys'] = []
      #self.book[symbol]['avgbookbuy'] = 0
      #count = 0
      for (price, size)in buyorders:
          self.book[symbol]['buys'].append((price,size))
          #self.book[symbol]['avgbookbuy'] = 
      self.book[symbol]['sells'] = []
      for (price, size) in sellorders:
          self.book[symbol]['sells'].append((price,size))
  
  def update_history(self, symbol, price):
      self.book[symbol]['history'].append(price)

class BaseBotClient(p.Protocol):

    def connectionMade(self):
        print 'hi'
        self._id = 0
        self.SendHello()
        self.d = {}
        self.b = localBook()
        self.SendBondOrder('BUY', 1003, 13)
    
 
    def dataReceived(self, dat):
        #print self.b.book
        datas = dat.split('\n')
        for data in datas:
          data = data.split(' ')
          if data[0] == 'BOOK':
              sym = data[1]
              bi = data.index('BUY')
              si = None
              pp = []
              for i in range(bi + 1, len(data)):
                  if data[i] == 'SELL':
                      si = i
                      break
                  p, s = data[i].split(':')
                  pp.append((int(p), int(s)))
              ss = []
              if si:
                  for i in range(si + 1, len(data)):
                      p, s = data[i].split(':')
                      ss.append((int(p), int(s)))
              self.b.book_message(sym, pp, ss)
          elif data[0] == 'TRADE':
              self.b.book[data[1]]['lasttradeprice'] = data[2]
              self.b.book[data[1]]['history'].append(data[2])
              #print self.b.book
          elif data[0] == 'FILL':
              if data[3] == 'BUY':
                self.b.book[data[2]]['holding'] += int(data[5])
                self.b.book[data[2]]['ourbuys'].append((data[4],data[5])) 
                self.b.book[data[2]]['history'].append(data[4])    
              elif data[3] == 'SELL':
                self.b.book[data[2]]['holding'] -= int(data[5])
                self.b.book[data[2]]['oursells'].append((data[4],data[5]))
                self.b.book[data[2]]['history'].append(data[4])        
          print self.b.book["BOND"]
          print ""

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
        price = 980
        for i in range(20):
            self.SendBondOrder('BUY', price + i, 1)

    def sendsellorders(self):
        price = 1001
        for i in range(20):
            self.SendBondOrder('SELL', price + i, 1)

class BaseBotFactory(p.ReconnectingClientFactory):

    protocol = BaseBotClient

    def __init__(self):
        pass

reactor.connectTCP(EXCHANGE_URL, 20001, BaseBotFactory())
reactor.run()
# #!/usr/bin/python
