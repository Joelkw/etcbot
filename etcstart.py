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
      localBook.rememberxlfprice = {"BOND":10000, "GS":10000, "MS":10000, "WFC":10000}

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
        #p iint self.b.book
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
              #pirint self.b.book
          elif data[0] == 'FILL':
              if data[3] == 'BUY':
                self.b.book[data[2]]['holding'] += int(data[5])
                self.b.book[data[2]]['ourbuys'].append((data[4],data[5])) 
                self.b.book[data[2]]['history'].append(data[4])   
                if data[2] == 'XLF':
                  self.SendXLFConvertOrder("SELL", 10)
                  #convert immediately and sell 
                  print "!XLF! Just converted an XLF!"
                  print "" 
              elif data[3] == 'SELL':
                self.b.book[data[2]]['holding'] -= int(data[5])
                self.b.book[data[2]]['oursells'].append((data[4],data[5]))
                self.b.book[data[2]]['history'].append(data[4]) 
                if data[2] == 'XLF':
                  # we need to immediately sell    
                  for stock in ["BOND", "MS"]:
                    self.SendOrder('ADD', symbol, "SELL", self.b.rememberxlfprice[symbol], 3)
                  for stock in ["GS", "WFC"]:
                    self.SendOrder('ADD', symbol, "SELL", self.b.rememberxlfprice[symbol], 2)
                    print "Selling ", symbol, "at ", self.b.rememberxlfprice[symbol], "!\n"
                  print "!XLF Just put out sells for the stocks!"
                  print "" 

          #print self.b.book["BOND"]
          bookabbr = self.b.book 
          Tenxlf  = self.GetXLFPackPrice()
          Tenxlfval = self.TenXLFValue()
          if ((Tenxlf+13) < Tenxlfval) and self.SpaceForXLFStocks() and ((Tenxlf+13)*10 > Tenxlfval):
            self.SendXLFOrder("BUY", Tenxlf/10 + 1, 10)
            print "!XLF! sent a buy order for 10 XLF at price", Tenxlf, "\n"
            print "the value of the 10 was ", Tenxlf, " and the value of the stocks was ", Tenxlfval
            print "\n"
          else:
            print "!XLF! value for 10 was ", Tenxlf, " and the value of the stocks was ", Tenxlfval, " so no buy!"
            print self.b.book["XLF"]

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

    def _SendXLFConvert(self, ty, sym, buy, size):
        uuid = self.GetUUID()
        self.d[uuid] = (buy, size)
        return self.Send(
                '{0} {1} {2} {3} {4}'.format(
                    ty, uuid, sym, buy, size))

    def SendOrder(self, *args, **kwargs):
        self._SendOrder(*args, **kwargs)

    def SendXLFConvert(self, *args, **kwargs):
        self._SendXLFConvert(*args, **kwargs)

    def SendBondOrder(self, buy, price, amount):
        self.SendOrder('ADD', 'BOND', buy, price , amount)

    # Gets the XLF price for 10 guaranteed
    def GetXLFPackPrice(self):
        count = 0
        returnprice = 10000000
        for (price, amount) in self.b.book["XLF"]["sells"]:
          count += amount 
          # need guaranteed price for all 
          returnprice = price
          if count >= 10:
            break
        #if count < 10:
         # returnprice = 1000000
        return (returnprice * 10)

    # gets the value of the stocks in it we could sell for
    def GetGuaranteedSellPrice(self, symbol, num):
        count = 0
        returnprice = 10000000
        for (price, amount) in self.b.book[symbol]["buys"]:
          count += amount 
          # need guaranteed price for all 
          returnprice = price
          if count >= num:
            break 
        self.b.rememberxlfprice[symbol] = returnprice
        if count < num:
            returnprice = 10000000
        return returnprice 

    def price_for_xlf(self, symbol):
      return self.b.book[symbol]['lasttradeprice']

    def TenXLFValue(self):
        print "Bond sell price for 3 was ", self.GetGuaranteedSellPrice("BOND", 3)
        print "GS sell price for 2 was ", self.GetGuaranteedSellPrice("GS", 2)
        print "MS sell price for 3 was ", self.GetGuaranteedSellPrice("MS", 3)
        print "WFC sell price for 2 was ", self.GetGuaranteedSellPrice("BOND", 2)
        return (self.GetGuaranteedSellPrice("BOND", 3) * 3 + self.GetGuaranteedSellPrice("GS", 2) * 2 + self.GetGuaranteedSellPrice("MS", 3) * 3 + self.GetGuaranteedSellPrice("WFC", 2) * 2)

    def SpaceForStock(self, symbol, amount):
      if self.b.book[symbol]['holding'] < amount:
        return True
      else:
        return False

    def SpaceForXLFStocks(self):
      if (self.SpaceForStock("BOND", 30)):
        if (self.SpaceForStock("MS", 30)):
          if (self.SpaceForStock("GS", 20)):
            if (self.SpaceForStock("WFC", 20)):
              return True
            else:
              return False
          else:
            return False
        else: 
          return False
      else:
        return False
        
    def SendXLFOrder(self, buy, price, amount):
        self.SendOrder('ADD', 'XLF', buy, price, amount)

    def SendXLFConvertOrder(self, buy, amount):
        self.SendXLFConvert('CONVERT', 'XLF', buy, amount)

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

reactor.connectTCP(EXCHANGE_URL, 20000, BaseBotFactory())
reactor.run()# #!/usr/bin/python
