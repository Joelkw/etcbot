# #!/usr/bin/python
# #test-exch-IMMEDEBUG.sf.js-etc has address 10.0.57.138
import sys
import socket
import uuid
import threading


from twisted.internet import reactor, protocol as p

TEAMNAME = 'IMMEDEBUG'
EXCHANGE_URL = 'test-exch-' + TEAMNAME.lower()
#EXCHANGE_URL='test-exch-IMMEDEBUG-0'
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
    	print data 
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

reactor.connectTCP(EXCHANGE_URL, 20001, BaseBotFactory())
reactor.run()

# symbols = ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]

# class localBook(object):
# 	def __init__(self):
# 		localBook.symbols = ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]
# 		# let book be current price, stock:[(price, amount)] 
# 		localBook.book = {}
# 		for symbol in localBook.symbols:
# 			localBook.book[symbol] = {'lasttradeprice': 1000000, 'size': 0, 'totalorders': 0, 'sells': [(0,0)], 'buys': [(0,0)], 'avgbookbuy': 0, 'avgbooksell': 0}

# 	def trade_message(self, symbol, price):
# 		self.book[symbol]['lasttradeprice'] = price

# 	# orders are lists of tuples (price, size)
# 	def book_message(self, symbol, buyorders, sellorders):
# 		# because books update and we don't want duplicates just take 15 best
# 		self.book[symbol]['buys'] = []
# 		#self.book[symbol]['avgbookbuy'] = 0
# 		#count = 0
# 		for (price, size)in buyorders:
# 			self.book[symbol]['buys'].append((price,size))
# 			#self.book[symbol]['avgbookbuy'] = 
# 		self.book[symbol]['sells'] = []
# 		for (price, size) in sellorders:
# 			self.book[symbol]['sells'].append((price,size))
# 		print "Logged"

# class ourOrders(object):
# 	def __init__(self):
# 		self.orders = {}
# 		for symbol in symbols:
# 			self.orders[symbol] = {'totalbuys': 0, 'totalsells': 0, 'buys': [(0,0)], 'sells': [(0,0)]}




# ourBook = localBook()
# ourBook.trade_message("BOND", 123)
# ourBook.book_message("BOND", [(124, 15), (135,24)], [(2323, 2)])
# print ourBook.book


