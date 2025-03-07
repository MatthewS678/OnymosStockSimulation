import threading
import random
import time

# HOW TO RUN: Can run with the command 'python OnymosStock.py' in the directory containing this file
# EXPECTED OUTPUT: Once run, you should see orders being added as output and periodic matching occuring displaying the current buy and sell orders 
# and which orders got matched. This will occur indefinitely until the user manually stops it.


class Order:
    def __init__(self, order_type, ticker, quantity, price):
        self.order_type = order_type
        self.ticker = ticker
        self.quantity = quantity
        self.price = price

class StockMarket:
    def __init__(self):
        self.orders = []
        self.lock = threading.Lock()

    def addOrder(self, order_type, ticker, quantity, price):
        order = Order(order_type, ticker, quantity, price)
        with self.lock:
            self.orders.append(order)
            print(f"Added: {order_type} {quantity} shares of {ticker} at ${price}")

    def matchOrder(self):
        with self.lock:
            # seperate buy and sell orders
            buy_orders = [order for order in self.orders if order.order_type == "Buy"]
            sell_orders = [order for order in self.orders if order.order_type == "Sell"]

            # sort orders by ticker for easier matching
            buy_orders.sort(key=lambda x: x.ticker)
            sell_orders.sort(key=lambda x: x.ticker)

            # prints the current buy and sell orders for reference
            print(f"Buy Orders: {[f'{order.ticker} {order.quantity} for ${order.price}' for order in buy_orders]}")
            print(f"Sell Orders: {[f'{order.ticker} {order.quantity} for ${order.price}' for order in sell_orders]}")

            i, j = 0, 0
            while i < len(buy_orders) and j < len(sell_orders):
                buy_order = buy_orders[i]
                sell_order = sell_orders[j]

                # if the ticker matches we need to find the lowest sell order price for that ticker
                if buy_order.ticker == sell_order.ticker:
                    matching_sell_orders = [order for order in sell_orders if order.ticker == buy_order.ticker]
                    lowest_sell_order = min(matching_sell_orders, key=lambda x: x.price)

                    # successfully match if the buy order's price is >= lowest sell price
                    if buy_order.price >= lowest_sell_order.price:
                        matched_quantity = min(buy_order.quantity, lowest_sell_order.quantity) # can only match the smaller number of the requested order type
                        print(f"Matched {matched_quantity} shares of {buy_order.ticker} at ${lowest_sell_order.price}")

                        # update quantities after transaction
                        buy_order.quantity -= matched_quantity
                        lowest_sell_order.quantity -= matched_quantity

                        # if a buy order is fully matched move to the next buy order
                        if buy_order.quantity == 0:
                            i += 1
                        # if a sell order is fully matched move to the next sell order
                        if lowest_sell_order.quantity == 0:
                            j += 1
                    else:
                        # no match if buy price is less than sell price so we move to next sell order
                        j += 1
                else:
                    # if tickers don't match try the next highest ticker number
                    if buy_order.ticker < sell_order.ticker:
                        i += 1
                    else:
                        j += 1

            # remove orders that have been fully matched
            self.orders = [order for order in self.orders if order.quantity > 0]

def simulateOrders(market):
    tickers = [f"ticker{i}" for i in range(1024)]
    while True:  # simulate orders forever until user input stops it
        ticker = random.choice(tickers)
        for _ in range(5): # create multiple orders with the same ticker to ensure matching is more likely to happen
            order_type = random.choice(["Buy", "Sell"])
            quantity = random.randint(1, 200)
            price = round(random.uniform(10, 300), 2)
            market.addOrder(order_type, ticker, quantity, price)
            time.sleep(0.5)  # pause between orders for readibility
        market.matchOrder() # try to match after adding new orders

if __name__ == "__main__":
    market = StockMarket()

    thread = threading.Thread(target=simulateOrders, args=(market,))
    thread.daemon = True  # makes the thread end when the main program ends isntead of waiting until completion
    thread.start()

    # keep the main thread running to allow simulation to continue forever
    while True:
        time.sleep(1)
