print('=' * 100)
import time
import os
import sys
import dateparser
import pytz
import json
import matplotlib.pyplot as plt
import mpl_finance #import candlestick_ohlc
from datetime import datetime
from binance.client import Client
from vault.BinanceKeys import BinanceKey1

class Trader():
    list_of_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT','BNBBTC', 'ETHBTC', 'LTCBTC']
    list_of_assets = []
    unit_BTC = 0.01
    unit_USDT = 10
    test_asset = 1

    def __init__(self, api_key, api_secret):
        """Binance API Client constructor
        :param api_key: Api Key
        :type api_key: str.
        :param api_secret: Api Secret
        :type api_secret: str.
        """
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.client = Client(api_key , api_secret)

    # Get open orders and print all orders to screen
    def get_open_orders(self, pair):
        """print out all open orders
        """
        orders = self.client.get_open_orders(symbol = pair)
        for x in range(len(orders)):
            if orders[x]['side'] == 'BUY':
                print('BUY')
                print(orders[x]['price'])

            else:
                print("SELL")
                print(orders[x]['price'])

        return orders

    # Get all open orders and print all orders to screen
    def get_all_open_orders(self):
        """print out all open orders
        """
        orders = self.client.get_open_orders()
        print(orders)
        for x in range(len(orders)):
            if orders[x]['side'] == 'BUY':
                print('Buy {} price {}'.format(orders[x]['symbol'] ,orders[x]['price']))

            else:
                print('Sell {} price {}'.format(orders[x]['symbol'] ,orders[x]['price']))

        if orders == []:
            print('there is NO open order!!')
        return orders

    def cancel_open_order(self, pair):
        """cancel one order of pair
        :param pair:
        :return:
        """
    def cancel_all_open_order(self):
        """cancel all open order
        :return:
        """
    def run(self):
        orders = self.get_all_open_orders()
        address = self.client.get_deposit_address(asset='BTC')
        # get a deposit address for BTC and check API key & connection
        print('Deposit address of {} is {}'.format(address['asset'] , address['address']) )
        print('=' * 100)
        # My_Deposit address of BTC is 1NsibSZoW3AfkrHp88khQguqrToRFh2CTx (^_^)
        status = self.client.get_system_status()
        print("\nExchange Status: ", status)
        print('=' * 100)
        #Account Withdrawal History Info
        withdraws = self.client.get_withdraw_history()
        withdraw_list = withdraws['withdrawList']
        print('=' * 100)
        for i in range(len(withdraw_list)):
            print("\nClient Withdraw History: ", withdraw_list[i]['amount'] , withdraw_list[i]['asset'])
        print('=' * 100)
        #Visualize candle history of list_of_coin
        for pair in self.list_of_symbols:
            self.show_historic_klines(pair, "1 month ago UTC", "now UTC", Client.KLINE_INTERVAL_1DAY)
            self.show_historic_klines(pair, "1 year ago UTC", "now UTC", Client.KLINE_INTERVAL_1WEEK)

    def sell_trader(self):
        """ find coint to sell
        :return: none
        """
        sell_list = []
        for coin in self.list_of_assets:
            if coin != 'BTC' and coin != 'USDT'and coin != 'ONG':
                pair = coin + 'BTC'
                asset_balance = self.client.get_asset_balance(coin)
                free_balance = float(asset_balance['free'])
                symbol_info = self.client.get_symbol_info(pair)
                print(symbol_info)
                min_quantity = float(symbol_info['filters'][1]['minQty'])
                print(min_quantity)

                if free_balance > min_quantity:
                    sell_list.append(coin)
        print('Sell list: {}'.format(sell_list))
        print("="*70)

        for coin in sell_list:
            if coin != 'BTC' and coin != 'USDT' and coin != 'ONG':
                pair = coin + 'BTC'
                self.show_historic_klines(pair, "1 month ago UTC", "now UTC", Client.KLINE_INTERVAL_1DAY)
                self.show_historic_klines(pair, "1 year ago UTC", "now UTC", Client.KLINE_INTERVAL_1WEEK)
                self.show_historic_klines(pair, "24 hours ago UTC", "now UTC", Client.KLINE_INTERVAL_15MINUTE)
                ask = int(input('Do you want to sell {} (Yes = 1)'.format(pair)))
                if ask == 1:
                    price = self.client.get_symbol_ticker(symbol=pair)
                    print(price)
                    x_price = float(price['price']) * 1.01
                    asset = self.client.get_asset_balance(asset=coin)
                    x_asset = float(asset['free'])
                    self.sell_order_btc(pair, price=x_price, quantity=x_asset)

                    print('sell order of {} was placed'.format(pair))

    def buy_trader(self):
        """ Find coin to buy
        :return: none
        """
    def market_depth(self, sym, num_entries=10):
        #Get market depth
        #Retrieve and format market depth (order book) including time-stamp
        i=0     #Used as a counter for number of entries
        print("Order Book: ", self.convert_time_binance(Client.get_server_time(self)))
        depth = Client.get_order_book(self, symbol=sym)
        print("\n", sym, "\nDepth     ASKS:\n")
        print("Price     Amount")
        for ask in depth['asks']:
            if i<num_entries:
                print(ask)
                i+=1
        j=0     #Secondary Counter for Bids
        print("\n", sym, "\nDepth     BIDS:\n")
        print("Price     Amount")
        for bid in depth['bids']:
            if j<num_entries:
                print(bid)
                j+=1

    def coin_prices(self, watch_list):
        #Will print to screen, prices of coins on 'watch list'
        #returns all prices
        prices = Client.get_all_tickers(self)
        print("\nSelected (watch list) Ticker Prices: ")
        for price in prices:
            if price['symbol'] in watch_list:
                print(price)
        return prices

    def coin_tickers(self, watch_list):
        # Prints to screen tickers for 'watch list' coins
        # Returns list of all price tickers
        tickers = Client.get_orderbook_tickers(self)
        print("\nWatch List Order Tickers: \n")
        for tick in tickers:
            if tick['symbol'] in watch_list:
                print(tick)
        return tickers

    def date_to_milliseconds(self, date_str):
        """Convert UTC date to milliseconds

        If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/

        :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
        :type date_str: str
        """
        # get epoch value in UTC
        epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
        # parse our date string
        d = dateparser.parse(date_str)
        # if the date is not timezone aware apply UTC timezone
        if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
            d = d.replace(tzinfo=pytz.utc)

        # return the difference in time
        return int((d - epoch).total_seconds() * 1000.0)


    def interval_to_milliseconds(self, interval):
        """Convert a Binance interval string to milliseconds

        :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
        :type interval: str

        :return:
             None if unit not one of m, h, d or w
             None if string not in correct format
             int value of interval in milliseconds
        """
        ms = None
        seconds_per_unit = {
            "m": 60,
            "h": 60 * 60,
            "d": 24 * 60 * 60,
            "w": 7 * 24 * 60 * 60
        }

        unit = interval[-1]
        if unit in seconds_per_unit:
            try:
                ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
            except ValueError:
                pass
        return ms


    def convert_time_binance(self, gt):
        #Converts from Binance Time Format (milliseconds) to time-struct
        #gt = client.get_server_time()
        print("Binance Time: ", gt)
        print(time.localtime())
        aa = str(gt)
        bb = aa.replace("{'serverTime': ","")
        aa = bb.replace("}","")
        gg=int(aa)
        ff=gg-10799260
        uu=ff/1000
        yy=int(uu)
        tt=time.localtime(yy)
        #print(tt)
        return tt


    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        """Get Historical Klines from Binance

        See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Biannce Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format
        :type start_str: str
        :param end_str: optional - end date string in UTC format
        :type end_str: str

        :return: list of OHLCV values

        """
        # create the Binance client, no need for api key
        client = Client("", "")

        # init our list
        output_data = []

        # setup the max limit
        limit = 500

        # convert interval to useful value in seconds
        timeframe = self.interval_to_milliseconds(interval)

        # convert our date strings to milliseconds
        start_ts = self.date_to_milliseconds(start_str)

        # if an end time was passed convert it
        end_ts = None
        if end_str:
            end_ts = self.date_to_milliseconds(end_str)

        idx = 0
        # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
        symbol_existed = False
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where our start date is before the symbol pair listed on Binance
            if not symbol_existed and len(temp_data):
                symbol_existed = True

            if symbol_existed:
                # append this loops data to our output data
                output_data += temp_data

                # update our start timestamp using the last value in the array and add the interval timeframe
                start_ts = temp_data[len(temp_data) - 1][0] + timeframe
            else:
                # it wasn't listed yet, increment our start date
                start_ts += timeframe

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(temp_data) < limit:
                # exit the while loop
                break

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)

        return output_data

    def save_historic_klines_csv(self, symbol, start, end, interval):
        klines = self.get_historical_klines(symbol, interval, start, end)
        ochl = []
        list_of_open = []
        three_period_moving_ave = []
        time3=[]
        five_period_moving_ave = []
        ten_period_moving_ave = []
        time10=[]
        with open('Binance_{}_{}-{}.txt'.format(symbol, start, end), 'w') as f:
            f.write('Time, Open, High, Low, Close, Volume\n')
            for kline in klines:
                #print(kline)
                time1 = int(kline[0])
                open1 = float(kline[1])
                Low = float(kline[2])
                High = float(kline[3])
                Close = float(kline[4])
                Volume = float(kline[5])
                format_kline = "{}, {}, {}, {}, {}, {}\n".format(time, open1, High, Low, Close, Volume)
                ochl.append([time1, open1, Close, High, Low, Volume])
                f.write(format_kline)

                #track opening prices, use for calculating moving averages
                list_of_open.append(open1)
                    #Calculate three 'period' moving average - Based on Candlestick duration
                if len(list_of_open)>2:
                    price3=0
                    for pri in list_of_open[-3:]:
                        price3+=pri
                    three_period_moving_ave.append(float(price3/3))
                    time3.append(time1)
                #Perform Moving Average Calculation for 10 periods
                if len(list_of_open)>9:
                    price10=0
                    for pri in list_of_open[-10:]:
                        price10+=pri
                    ten_period_moving_ave.append(float(price10/10))
                    time10.append(time1)

        #Matplotlib visualization how-to from: https://pythonprogramming.net/candlestick-ohlc-graph-matplotlib-tutorial/
        fig, ax = plt.subplots()
        mpl_finance.candlestick_ochl(ax, ochl, width=1)
        plt.plot(time3, three_period_moving_ave, color='green', label='3 Period MA - Open')
        plt.plot(time10, ten_period_moving_ave, color='blue', label='10 Period MA - Open')
        #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d-%h-%m')) #Converting to date format not working
        ax.set(xlabel='Date', ylabel='Price', title='{} {}-{}'.format(symbol, start, end))
        plt.legend()
        plt.show()

    def show_historic_klines(self, symbol, start, end, interval):
        klines = self.get_historical_klines(symbol, interval, start, end)
        ochl = []
        list_of_open = []
        three_period_moving_ave = []
        time3 = []
        five_period_moving_ave = []
        ten_period_moving_ave = []
        time10 = []
        for kline in klines:
            # print(kline)
            time1 = int(kline[0])
            open1 = float(kline[1])
            Low = float(kline[2])
            High = float(kline[3])
            Close = float(kline[4])
            Volume = float(kline[5])
            ochl.append([time1, open1, Close, High, Low, Volume])
            # track opening prices, use for calculating moving averages
            list_of_open.append(open1)

            # Calculate three 'period' moving average - Based on Candlestick duration
            if len(list_of_open) > 2:
                price3 = 0
                for pri in list_of_open[-3:]:
                    price3 += pri
                three_period_moving_ave.append(float(price3 / 3))
                time3.append(time1)
            # Perform Moving Average Calculation for 10 periods
            if len(list_of_open) > 9:
                price10 = 0
                for pri in list_of_open[-10:]:
                    price10 += pri
                ten_period_moving_ave.append(float(price10 / 10))
                time10.append(time1)

        # Matplotlib visualization how-to from: https://pythonprogramming.net/candlestick-ohlc-graph-matplotlib-tutorial/
        fig, ax = plt.subplots()
        mpl_finance.candlestick_ochl(ax, ochl, width=1)
        plt.plot(time3, three_period_moving_ave, color='green', label='3 Period MA - Open')
        plt.plot(time10, ten_period_moving_ave, color='blue', label='10 Period MA - Open')
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d-%h-%m')) #Converting to date format not working
        ax.set(xlabel='Date', ylabel='Price', title='{} {}-{}'.format(symbol, start, end))
        plt.legend()
        plt.show()

    def save_historic_klines_datafile(self, symbol, start, end, interval):
        #Collects kline historical data , output and saves to file
        klines = self.get_historical_klines(symbol, interval, start, end)

        # open a file with filename including symbol, interval and start and end converted to milliseconds
        with open(
            "Binance_{}_{}_{}-{}_{}-{}.json".format(
                symbol,
                interval,
                start,
                end,
                self.date_to_milliseconds(start),
                self.date_to_milliseconds(end)
            ),
            'w'  # set file write mode
        ) as f:
            f.write(json.dumps(klines))

    def get_symbol_info(self, symbol):
        """Return information about a symbol

        :param symbol: required e.g BNBBTC
        :type symbol: str

        :returns: Dict if found, None if not

        .. code-block:: python

            {
                "symbol": "ETHBTC",
                "status": "TRADING",
                "baseAsset": "ETH",
                "baseAssetPrecision": 8,
                "quoteAsset": "BTC",
                "quotePrecision": 8,
                "orderTypes": ["LIMIT", "MARKET"],
                "icebergAllowed": false,
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.00000100",
                        "maxPrice": "100000.00000000",
                        "tickSize": "0.00000100"
                    }, {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00100000",
                        "maxQty": "100000.00000000",
                        "stepSize": "0.00100000"
                    }, {
                        "filterType": "MIN_NOTIONAL",
                        "minNotional": "0.00100000"
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        infor = self.client.get_symbol_info(symbol)

        return infor

    # place a buy order if we have enought money
    def buy_order_btc(self, asset, price):
        """place a buy order, use BTC to buy an asset
        :param asset: required e.g 'ETCBTC'
        :param price: required 0.0056
        :return:
        """
        precision_asset = 8
        precision_unit = 8

        symbol_info = self.get_symbol_info(asset)
        quoteAsset = symbol_info['quoteAsset']
        baseAsset = symbol_info['baseAsset']
        price_fileter = float(symbol_info['filters'][0]['tickSize'])
        for i in range(1 , 9):
            n = price_fileter*(10**i)
            if n == 1:
                precision_asset = i
        price_to_buy = "{:0.0{}f}".format(price, precision_asset)  # price of asset in format
        print(price_to_buy)

        unit_asset = self.unit_BTC/price
        unit_fileter = float(symbol_info['filters'][1]['minQty'])
        for i in range(1 , 9):
            n = unit_fileter*(10**i)
            if n == 1:
                precision_unit = i
        unit_to_buy = "{:0.0{}f}".format(unit_asset, precision_unit)  # unit of asset in format
        print(unit_to_buy)

        money = self.client.get_asset_balance(asset=quoteAsset)
        float_currency = float(money['free'])
        if float_currency >= self.unit_BTC:
            print('Quanlity of {} is {} and we have enought to buy {} of {}'.format(quoteAsset, float_currency,
                                                                                    unit_to_buy, baseAsset))

            if self.test_asset == 0:

                order = self.client.order_limit_buy(
                    symbol=asset,						#:param symbol: required
                    quantity=unit_to_buy,				#:param quantity: required, :type quantity: decimal
                    price=price_to_buy,)					#:param price: required,	:type price: str

                print('BUY order was placed, price {} and quantity of {} is {} '.format(amt_str, asset, unit_to_buy))
            else:
                order = self.client.create_test_order(
                    symbol=asset,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=unit_to_buy,
                    price=price_to_buy)

                print('test BUY order is done, test_asset = 1')
        else:
            print('Quantity of {} is {} and we have NOT enough to buy {} of {}'.format(quoteAsset, float_currency,
                                                                                    unit_to_buy, baseAsset))

    def sell_order_btc(self, asset, price, quantity):
        """place a sell order, sell an asset and take BTC
        :param asset: required e.g 'ETCBTC'
        :param price: required 0.0056
        :return:
        """
        precision_asset = 8
        precision_unit = 8

        symbol_info = self.get_symbol_info(asset)
        baseAsset = symbol_info['baseAsset']
        price_fileter = float(symbol_info['filters'][0]['tickSize'])
        for i in range(1, 9):
            n = price_fileter * (10 ** i)
            if n == 1:
                precision_asset = i
        price_to_sell = "{:0.0{}f}".format(price, precision_asset)  # price of asset in format
        print(price_to_sell)

        quantity_fileter = float(symbol_info['filters'][1]['minQty'])
        for i in range(1, 9):
            n = quantity_fileter * (10 ** i)
            if n == 1:
                precision_unit = i
        quantity_to_sell = "{:0.0{}f}".format(quantity, precision_unit)  # quantity of asset in format
        print(quantity_to_sell)

        current_asset = self.client.get_asset_balance(asset=baseAsset)
        float_asset = float(current_asset['free'])
        if float_asset >= quantity:
            print('Quantity of {} is {} and we have enough to sell {} of {}'.format(baseAsset, float_asset,
                                                                                     quantity_to_sell, baseAsset))
            if self.test_asset == 0:
                order = self.client.order_limit_sell(
                    symbol=asset,                   #:param symbol: required
                    quantity=quantity_to_sell,      #:param quantity: required, :type quantity: decimal
                    price=price_to_sell, )          #:param price: required,	:type price: str

                print('sell order was placed, price {} and quantity of {} is {} '.format(price_to_sell, asset,
                                                                                         quantity_to_sell))
            else:
                order = self.client.create_test_order(
                    symbol=asset,
                    side=self.client.SIDE_SELL,
                    type=self.client.ORDER_TYPE_LIMIT,
                    timeInForce=self.client.TIME_IN_FORCE_GTC,
                    quantity=quantity_to_sell,
                    price=price_to_sell)

                print('test sell order is done, test_asset = 1')
        else:
            print('Quantity of {} is {} and we have NOT enough to sell {} of {}'.format(baseAsset, float_asset,
                                                                                         quantity_to_sell, baseAsset))

    def get_asset_balance(self):
        """Get current asset balance.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data

        :param asset: required
        :type asset: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: dictionary or None if not found

        .. code-block:: python

            {
                "asset": "BTC",
                "free": "4723846.89208129",
                "locked": "0.00000000"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return  self.client.get_asset_balance(asset)

    def get_account(self):
        """Get current account information.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data

        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "makerCommission": 15,
                "takerCommission": 15,
                "buyerCommission": 0,
                "sellerCommission": 0,
                "canTrade": true,
                "canWithdraw": true,
                "canDeposit": true,
                "balances": [
                    {
                        "asset": "BTC",
                        "free": "4723846.89208129",
                        "locked": "0.00000000"
                    },
                    {
                        "asset": "LTC",
                        "free": "4763368.68006011",
                        "locked": "0.00000000"
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        account = self.client.get_account()
        for i in range(len(account['balances'])):
            x = float(account['balances'][i]['free']) + float(account['balances'][i]['locked'])
            if x > 0:
                asset = account['balances'][i]['asset']
                self.list_of_assets.append(asset)
                print(account['balances'][i])

        return account

def main():
    trade = Trader(api_key = BinanceKey1['api_key'], api_secret = BinanceKey1['api_secret'])
#    trade = Trader(api_key = BinanceKey2['api_key'], api_secret = BinanceKey2['api_secret'])
    print('=' * 100)
    for pair in trade.list_of_symbols:
        infor = trade.get_symbol_info(pair)
        print(infor)

    print('=' * 100)
    print(trade.get_account())
    print('=' * 100)
    print(trade.list_of_assets)
    trade.sell_trader()
#    trade.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
