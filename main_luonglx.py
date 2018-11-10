# Binance API api_key 	||| 	version v1.0.1   	|||   	Aug 2018					||
# luonglx@				|||		There are some flexiblein Up and Down percent_change	||
# ================================================================================================================

import sys
import time

'''Making unverified HTTPS requests is strongly discouraged, however,
if you understand the risks and wish to disable these warnings,
you can use disable_warnings():'''

import urllib3
urllib3.disable_warnings()

from binance.client import Client
from vault.BinanceKeys import BinanceKey1
api_key1 = BinanceKeys1.api_key
api_secret1 = BinanceKey1.api_secret


# decide what pair do you want to trade
# ======================================================================================
pair = ['ETCUSDT', 'NEOBTC', 'IOTAUSDT', 'NANOBTC']

ignor_command = [1, 1, 2, 1] 			# number of "don't care commands" remaining
# because sometime it don't excute for a long time

unit_asset = [3, 5, 50, 20]			# Block of asset to trade

precision_asset = [4, 6, 4, 7]			# work with asset_currency

asset = ['ETC', 'NEO', 'IOTA'	, 'NANO']			# first is asset and then is

currency = ['USDT', 'BTC', 'USDT', 'BTC']		# money base - to work exactly


# ====================================================================================================

# Minhky Account
# ====================================================================================================
pair1 = ['ETCBTC', 'NEOBTC', 'IOTABTC', 'ETHBTC', 'XMRBTC']

ignor_command1 = [0, 0, 1, 0, 1] 			# number of "don't care commands" remaining
# because sometime it don't excute for a long time

unit_asset1 = [3, 5, 50, 0.2, 0.1]			# Block of asset to trade

precision_asset1 = [6, 6, 6, 6, 6]			# work with asset_currency

asset1 = ['ETC', 'NEO', 'IOTA', 'ETH', 'XMR']			# first is asset and then is

currency1 = ['BTC', 'BTC', 'BTC', 'BTC', 'BTC']		# money base - to work exactly

# ====================================================================================================

period = 2					# time to sleep

timeout = 20000				# it will wait to connect about 5hours


test_asset = 0				# = 0 if make a real


up_percent = 1.02			# rate of SELL and BUY
dn_percent = 0.98			# orders

# Get all open orders and print all orders to screen

# ====================================================================================================
# print out all open orders
def get_open_orders(api_key, api_secret, pair):
    client = Client(api_key, api_secret, {"verify": False, "timeout": timeout})
    orders = client.get_open_orders(symbol=pair)

    for x in range(len(orders)):

        if orders[x]['side'] == 'BUY':
            print('BUY')
            print(orders[x]['price'])

        else:
            print("SELL")
            print(orders[x]['price'])

    return orders

# ====================================================================================================
# place a sell order if we have enought asset
def sell_order(api_key, api_secret, pair, unit_asset, precision_asset, price, asset, currency):
    client = Client(api_key, api_secret, {"verify": False, "timeout": timeout})

    amt_str = "{:0.0{}f}".format(price, precision_asset)
    print(amt_str)
    num_asset = client.get_asset_balance(asset)
    float_asset = float(num_asset['free'])

    if float_asset >= unit_asset:
        print('Quanlity of asset is {} and we have enought to sell {} of {}'.format(
            float_asset, unit_asset, asset))

        if test_asset == 0:

            order = client.order_limit_sell(
                symbol=pair,  # :param symbol: required
                quantity=unit_asset,  # :param quantity: required, :type quantity: decimal
                price=amt_str,)  # :param price: required,	:type price: str

            print('SELL order was placed, price {} and quantity of {} is {} '.format(
                amt_str, asset, unit_asset))
        else:
            print('SELL is not done, test_asset = 1')
    else:
        print('Quanlity of asset is {} and we have NOT enought to sell {} of {}'.format(
            float_asset, unit_asset, asset))

# ====================================================================================================
# caculate how much will we trade and the price of buy and sell
def caculate_percent(pair):
    client = Client(api_key, api_secret, {"verify": False, "timeout": timeout})
    klines = client.get_ticker(symbol=pair)

    global up_percent, dn_percent

    percent_change = float(klines['priceChangePercent'])
    if percent_change < -20:

        up_percent = 1.1
        dn_percent = 0.9

        print('Down to0 much: ')

    elif percent_change < -10:

        up_percent = 1.03
        dn_percent = 0.95

        print('Down 10 to 20 %')

    elif percent_change < -5:

        up_percent = 1.02
        dn_percent = 0.97

        print('Down 5 to 10 %')

    elif percent_change < 0:

        up_percent = 1.01
        dn_percent = 0.98

        print('Down in rank 5 %')

    elif percent_change < 5:

        up_percent = 1.02
        dn_percent = 0.99

        print('Up in rank 5 %')

    elif percent_change < 10:

        dn_percent = 1.03
        dn_percent = 0.98
        print('Up in rank 5 to 10 %')

    elif percent_change < 20:

        up_percent = 1.05
        dn_percent = 0.97
        print('Up in rank 10 to 20 %')

    else:
        up_percent = 1.1
        dn_percent = 0.9
        print('Up too much')
#	cacal = (up_percent , dn_percent)

    print('up_percent is {} and dn_percent is {}'.format(up_percent, dn_percent))
    return up_percent
    pass

# ====================================================================================================
# fishinh stratergy
def main_fishing(api_key, api_secret, pair, unit_asset, ignor_command, precision_asset, asset, currency):

    client = Client(api_key, api_secret, {"verify": False, "timeout": timeout})

    price = client.get_symbol_ticker(symbol=pair)
    print("Price of {} is :  {}".format(price['symbol'], price['price']))

    orders = get_open_orders(api_key, api_secret, pair)

    if len(orders) <= ignor_command:
        print('remaining only ignore commands')
        print("we are caculating the price of ask and bid, wait 1 minute")
        price_of_asset = float(price['price'])

        minn = maxx = price_of_asset
#		maxx = price_of_asset

        for x in xrange(1, 10):

            price = client.get_symbol_ticker(symbol=pair)
            current_of_asset = float(price['price'])
            minn = min(current_of_asset, minn)
            maxx = max(current_of_asset, maxx)

            time.sleep(period)
            print('*' * x)

        print(minn, maxx)

        cacul = caculate_percent(pair)

        print(cacul)

        print('Now we will place 2 orders, one BUY at {} and one SELL at {}'.format(
            minn*dn_percent, maxx*up_percent))

        # place SELL and BUY orders
        buy_order(api_key, api_secret, pair, unit_asset,
                  precision_asset, minn*dn_percent, asset, currency)
        sell_order(api_key, api_secret, pair, unit_asset,
                   precision_asset, maxx*up_percent, asset, currency)

    print('=' * 11)
    time.sleep(period)

# ====================================================================================================
# which stratergy will we use
def main():
    while True:
        for x in xrange(len(pair)):
            main_fishing(api_key1, api_secret1, pair[x], unit_asset[x],
                         ignor_command[x], precision_asset[x], asset[x], currency[x])
            pass
        for x in xrange(len(pair1)):
            main_fishing(api_key2, api_secret2, pair1[x], unit_asset1[x],
                         ignor_command1[x], precision_asset1[x], asset1[x], currency1[x])
    print('OK, done !!!')
    pass

# ====================================================================================================
# run
if __name__ == '__main__':
    main()
# the end !!!!!!!!!!!!
# =========================
# 28 Aug 2018 done    	||
# 10 Nov 2018   					||
# =========================
