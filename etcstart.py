# #!/usr/bin/python
# #test-exch-IMMEDEBUG.sf.js-etc has address 10.0.57.138
from __future__ import print_function

import sys
import socket

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("test-exch-IMMEDEBUG", 20001))
    return s.makefile('w+', 1)

def main():
    exchange = connect()
    print("HELLO TEAMNAME", file=exchange)
    hello_from_exchange = exchange.readline().strip()
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

if __name__ == "__main__":
    main()

#sendall() sends data exchange s.sendall() or exchange.sendall()
#exchange.recv()

symbols = ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]

class localBook(object):
	def __init__(self):
		localBook.symbols = ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]
		# let book be current price, stock:[(price, amount)] 
		localBook.book = {}
		for symbol in localBook.symbols:
			localBook.book[symbol] = {'lasttradeprice': 1000000, 'size': 0, 'totalorders': 0, 'sells': [(0,0)], 'buys': [(0,0)], 'avgbookbuy': 0, 'avgbooksell': 0}

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

class ourOrders(object):
	def __init__(self):
		self.orders = {}
		for symbol in symbols:
			self.orders[symbol] = {'totalbuys': 0, 'totalsells': 0, 'buys': [(0,0)], 'sells': [(0,0)]}




ourBook = localBook()
ourBook.trade_message("BOND", 123)
ourBook.book_message("BOND", [(124, 15), (135,24)], [(2323, 2)])
print ourBook.book


