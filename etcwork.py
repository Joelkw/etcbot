import sys
import socket
import uuid
import threading
import numpy as np 
import math

from twisted.internet import reactor, protocol as p

TEAMNAME = 'IMMEDEBUG'
#EXCHANGE_URL = 'test-exch-' + TEAMNAME.lower()
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

class localBook(object):
  def __init__(self):
      localBook.symbols = ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]
      # let book be current price, stock:[(price, amount)] 
      # history is a list of historical averages
      localBook.book = {}
      for symbol in localBook.symbols:
          localBook.book[symbol] = {'lasttradeprice': 1000000, 'size': 0, 'totalorders': 0, 'oursells': [], 'ourbuys':[], 'sells': [(0,0)], 'buys': [(0,0)], 'avgbookbuy': 0, 'avgbooksell': 0, 'holding': 0, 'history': [], 'value': 0, 'value-old': 0}
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
    
 
    def dataReceived(self, dat):
        print self.b.book
        datas = dat.split('\n')
        for data in datas:
          data = data.split(' ')
          #print data[0]
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
          #place highest sell order
              # print self.b.book[sym]
            # if we already bought it
              #TRADING START
              #self.SellAndHold()
              for sym in self.b.symbols:
                self.TrendTrade(sym)
                self.CrazyTrade(sym)
              #self.MakeObviousSale()
              #self.GetTrend("GS")
              #self.GetTrend("MS")
              """if sym not in ['BOND', 'XLF']:
                 (sprice, samount) = self.GetMostAgressive(sym, "SELL")
                 (bprice, bamount) = self.GetMostAgressive(sym, "BUY")
                 self.SendOrder("ADD", sym, "BUY", bprice, bamount)
                 self.SendOrder("ADD", sym, "SELL", sprice, samount)"""
          if data[0] == 'TRADE':
              #print "trade logged!"
              self.b.book[data[1]]['lasttradeprice'] = data[2]
              self.b.book[data[1]]['history'].append(data[2])
              #print "appended ",  data[2], " to history of ", data[1]
              #pirint self.b.book
          if data[0] == 'FILL':
              if data[3] == 'BUY':
                self.b.book[data[2]]['holding'] += int(data[5])
                self.b.book[data[2]]['ourbuys'].append((data[4],data[5])) 
                self.b.book[data[2]]['history'].append(data[4])   
                print "appended ",  data[4], " to history of ", data[2]
                """if data[2] == 'XLF':
                  self.SendXLFConvertOrder("SELL", 10)
                  #convert immediately and sell 
                  #print "!XLF! Just converted an XLF!"
                  #print """
              elif data[3] == 'SELL':
                self.b.book[data[2]]['holding'] -= int(data[5])
                self.b.book[data[2]]['oursells'].append((data[4],data[5]))
                self.b.book[data[2]]['history'].append(data[4]) 
                """if data[2] == 'XLF':
                  # we need to immediately sell    
                  for stock in ["BOND", "MS"]:
                    self.SendOrder('ADD', stock, "SELL", self.b.rememberxlfprice[stock], 3)
                  for stock in ["GS", "WFC"]:
                    self.SendOrder('ADD', stock, "SELL", self.b.rememberxlfprice[stock], 2)
                    #print "Selling ", symbol, "at ", self.b.rememberxlfprice[symbol], "!\n"
                  #print "!XLF Just put out sells for the stocks!"
                 # print """

          #print self.b.book["BOND"]
          """bookabbr = self.b.book 
          Tenxlf  = self.GetXLFPackPrice()
          Tenxlfval = self.TenXLFValue()
          if ((Tenxlf+13) < Tenxlfval) and self.SpaceForXLFStocks() and ((Tenxlf+13)*10 > Tenxlfval):
            self.SendXLFOrder("BUY", Tenxlf/10 + 1, 10)
            print "!XLF! sent a buy order for 10 XLF at price", Tenxlf, "\n"
            print "the value of the 10 was ", Tenxlf, " and the value of the stocks was ", Tenxlfval
            print "\n"
         # else:
            #print "!XLF! value for 10 was ", Tenxlf, " and the value of the stocks was ", Tenxlfval, " so no buy!"
            #print self.b.book["XLF"]"""

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
#        print "Bond sell price for 3 was ", self.GetGuaranteedSellPrice("BOND", 3)
#        print "GS sell price for 2 was ", self.GetGuaranteedSellPrice("GS", 2)
#        print "MS sell price for 3 was ", self.GetGuaranteedSellPrice("MS", 3)
#        print "WFC sell price for 2 was ", self.GetGuaranteedSellPrice("BOND", 2)
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

    def GetMostAgressive(self, sym, buy):
        if buy == "BUY":
            if self.b.book[sym]["buys"]:    
                return self.b.book[sym]["buys"][-1]
            else:
                return (0,0)
        if buy == "SELL":
            if self.b.book[sym]["sells"]:
                return self.b.book[sym]["sells"][-1]
            else:
                return (0,0)
    
    def GetLeastAgressive(self, sym, buy):
        if buy == "BUY":
            if self.b.book[sym]["buys"]:
                return self.b.book[sym]["buys"][0]
            else:
                return (0,0)
        if buy == "SELL":
            if self.b.book[sym]["sells"]:
                return self.b.book[sym]["sells"][0]
            else:
                return (0,0)
    
    def MakeObviousSale(self):
        #for our buys
        for sym in self.b.symbols:  
            if self.b.book[sym]['ourbuys']:
                 (offerprice, offeramount) = self.GetLeastAgressive(sym, "BUY" )
                 for (obprice, obamount) in self.b.book[sym]['ourbuys']:
                    if obprice < offerprice and obprice is not 0:
                          self.SendOrder("ADD", sym, "SELL", offerprice, min(obamount, offeramount))
                          print "Sell ", sym, " for ", min(obamount,offeramount), "oba: ", obamount, "ofa:", offeramount
                          break
            if self.b.book[sym]['oursells']:
                (offerprice, offeramount) = self.GetLeastAgressive(sym, "SELL" )
                for (osprice, osamount) in self.b.book[sym]['oursells']:
                     if osprice > offerprice:
                          self.SendOrder("ADD", sym, "BUY", offerprice, min(osamount, offeramount))
                          print "Buy ", sym, " for ", min(obamount,offeramount), "osa: ", osamount, "ofa:", offeramount
                          break

    def MakeProfit(self, minprofit):
          for sym in self.b.symbols:
            if self.b.book[sym]['ourbuys']:
                 (offerprice, offeramount) = self.GetLeastAgressive(sym, "BUY" )
                 for (obprice, obamount) in self.b.book[sym]['ourbuys']:
                    if obprice < offerprice + minprofit:
                          self.SendOrder("ADD", sym, "SELL", offerprice, min(obamount, offeramount))
                          break
            if self.b.book[sym]['ourbuys']:
                (offerprice, offeramount) = self.GetLeastAgressive(sym, "SELL" )
                for (osprice, osamount) in self.b.book[sym]['oursells']:
                     if osprice < offerprice + minprofit:
                          self.SendOrder("ADD", sym, "SELL", offerprice, min(osamount, offeramount))
                          break 
    def BuyAndHold(self):
        for sym in self.b.symbols:
            (offerprice, offeramount) = self.GetLeastAgressive(sym, "SELL")
            self.SendOrder("ADD", sym, "BUY", offerprice, 10)
        
    def SellAndHold(self):
        for sym in self.b.symbols:
            (offerprice, offeramount) = self.GetLeastAgressive(sym, "BUY")
            self.SendOrder("ADD", sym, "SELL", offerprice, 10)

    def sendbuyorders(self):
        price = 980
        for i in range(20):
            self.SendBondOrder('BUY', price + i, 1)

    def sendsellorders(self):
        price = 1001
        for i in range(20):
            self.SendBondOrder('SELL', price + i, 1)

    def PortfolioVal(self, sym):
        value = 0
        amount = self.b.book[sym]['holding']
        price = self.GetGuaranteedSellPrice(sym, amount)
        value += amount
        self.b.book[sym]['value'] = value
        return value

    def GetTrend(self, sym):
        length = len(self.b.book[sym]['history'])
        if length > 5:

            y = self.b.book[sym]['history'][0:min(length,15)]    
            N = int(len(y))
            x = range(N)
            B = (sum(int(x[i]) * int(y[i]) for i in xrange(N)) - 1./N*sum(x)*sum(int(y[i]) for i in range(len(y)))) / (sum(int(x[i])**2 for i in xrange(N)) - 1./N*sum(x)**2)
            A = 1.*sum(int(y[i]) for i in range(len(y)))/N - B * 1.*sum(x)/N
            print "trend for ", sym, " was ",  B
            return (B, min(length,15))
            #data = self.b.book[sym]['history'][0:min(length,15)]
            #x = np.arange(0,len(data))  
            #y=np.array(data)
            #z = np.polyfit(x,y,1)
            #print "{0}x + {1}".format(*z)            
            #print sym, " trending: {0}".format(*z)
            #print z[0]
        else:
            print "not enough history, len was: ", length
            print self.b.book[sym]['history']
            return (0,0)   

    def TrendTrade(self, sym):
        (trend, conf) = self.GetTrend(sym)
        if trend * conf > 8:
                # stock is trending up
                self.SendOrder("ADD", sym, "BUY", self.b.book[sym]['lasttradeprice'], 10)
        elif trend * conf < -8:
                self.SendOrder("ADD", sym, "SELL", self.b.book[sym]['lasttradeprice'], 10)

    def CrazyTrade(self, sym):
        (price,amount) = self.GetLeastAgressive(sym, "SELL")
        self.SendOrder("ADD", sym, "SELL", price+1, 10)
        (price,amount) = self.GetLeastAgressive(sym, "BUY")
        self.SendOrder("ADD", sym, "BUY", price-1, 10)


class BaseBotFactory(p.ReconnectingClientFactory):

    protocol = BaseBotClient

    def __init__(self):
        pass

reactor.connectTCP(EXCHANGE_URL, 20000, BaseBotFactory())
reactor.run()# #!/usr/bin/python
