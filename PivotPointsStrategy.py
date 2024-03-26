import Classes, pandas as pd
import datetime
import config

while True:
        symbols = []
        exchange = 'nasdaq'
        orderbyfield = ''
        direction = ''
        visiblecolumns = 'Symbol'
        industry = 'Technology'
        pricemin = 0
        pricemax = 1
        for i in range(2):
                skip = i*25
                url = 'https://www.marketwatch.com/tools/screener/stock?exchange={}&skip={}&orderbyfield={}&direction={}&visiblecolumns={}&industry={}&pricemin={}&pricemax={}'. format(exchange, skip, orderbyfield, direction, visiblecolumns, industry, pricemin, pricemax)
                df = pd.read_html(url, header=0)
                df = df[0]
                for item in df.loc[:,'Symbol'].tolist():
                        symbols.append(item)
   
        for symbol in symbols:
                security = Classes.Security(symbol, config.API_KEY, config.SECRET_KEY)
                print(symbol)
                if security.sell_at_day_end == True:
                        security.close_position()
                if security.analysable == True:
                        print(symbol)
                        security.get_pivot_points()
                        security.get_position_qty(security.support_break_point)
                        if security.latest_minute_bar_close < security.resistance_break_point and  security.previous_minute_bar_close >= security.resistance_break_point and security.owned() == True and security.bought() == False:
                                print(security.close_position())
                        if security.latest_minute_bar_close > security.support_break_point and security.previous_minute_bar_close <= security.support_break_point and security.owned() == False and security.bought() == False:
                                if security.sold() == True:
                                        security.cancel_order('open', 'sell', 'desc')
                                print(security.create_side_order(security.position_qty, 'buy', 'market', 'day'))
                                if security.stopped() == False:
                                        print(security.create_stop_order(security.position_qty, 'sell', 'stop', 'day', (round(security.support_break_point,2))))