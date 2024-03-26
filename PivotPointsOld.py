
import option_history.config as config, pandas as pd, os, glob, datetime

short_timeframe = 1
short_timeframe_string = str(short_timeframe) + 'Min'

long_timeframe = 1
long_timeframe_string = str(long_timeframe) + 'Day'

#holdings = open('data/qqq.csv').readlines()
#symbols = [holding.split(',')[2].strip() for holding in holdings][1:]
#string_symbols =  ','.join(symbols)

while True:

    market_open = False
    num_of_seconds = (datetime.datetime.utcnow().hour*60*60)+(datetime.datetime.utcnow().minute*60)+(datetime.datetime.utcnow().second)
    week_day = datetime.datetime.today().weekday()

    if num_of_seconds >= 52200 and num_of_seconds <= 75600 and week_day < 5:
        market_open=True

    while market_open == True:

        if num_of_seconds >= 75400:
            for symbol in symbols:
                position = config.get_positions(symbol)
                if 'asset_id' in position:
                    config.close_position(symbol)

        if num_of_seconds < 52200 or num_of_seconds > 75600:
            market_open=False

        exchange = 'nasdaq'
        skip = 0
        orderbyfield = ''
        direction = ''
        visiblecolumns = 'Symbol'
        industry = 'Technology'
        pricemin = 0
        pricemax = 1
        url = 'https://www.marketwatch.com/tools/screener/stock?exchange={}&skip={}&orderbyfield={}&direction={}&visiblecolumns={}&industry={}&pricemin={}&pricemax={}'. format(exchange, skip, orderbyfield, direction, visiblecolumns, industry, pricemin, pricemax)
        df = pd.read_html(url, header=0)
        df = df[0]
        symbols = df.loc[:,'Symbol'].tolist()
        skip = 25
        url = 'https://www.marketwatch.com/tools/screener/stock?exchange={}&skip={}&orderbyfield={}&direction={}&visiblecolumns={}&industry={}&pricemin={}&pricemax={}'. format(exchange, skip, orderbyfield, direction, visiblecolumns, industry, pricemin, pricemax)
        df2 = pd.read_html(url, header=0)
        df2 = df2[0]
        for item in df2.loc[:,'Symbol'].tolist():
            symbols.append(item)
        string_symbols =  ','.join(symbols)

        now = datetime.datetime.utcnow()
        if (now.minute % short_timeframe == 0) and (now.second == 0):

            files = glob.glob('data/bars/*.txt')
            for f in files:
                os.remove(f)

            short_bars_data = config.get_bars(string_symbols, short_timeframe_string, 10000)
            for symbol in short_bars_data['bars']:
                filename = 'data/bars/{}_short_bars.txt'.format(symbol)
                f = open(filename, 'w+')
                f.write('Date,Open,High,Low,Close,Volume,OpenInterest\n')
                for bar in short_bars_data['bars'][symbol]:
                    line = '{},{},{},{},{},{},{}\n'.format(bar['t'],bar['o'],bar['h'],bar['l'],bar['c'],bar['v'], 0.00)
                    f.write(line)
                
            long_bars_data = config.get_bars(string_symbols, long_timeframe_string, 100)
            for symbol in long_bars_data['bars']:
                filename = 'data/bars/{}_long_bars.txt'.format(symbol)
                f = open(filename, 'w+')
                f.write('Date,Open,High,Low,Close,Volume,OpenInterest\n')
                for bar in long_bars_data['bars'][symbol]:
                    line = '{},{},{},{},{},{},{}\n'.format(bar['t'],bar['o'],bar['h'],bar['l'],bar['c'],bar['v'], 0.00)
                    f.write(line)
                
            for symbol in short_bars_data['bars']:
                if os.path.exists('data/bars/{}_long_bars.txt'.format(symbol)):
                    if os.stat('data/bars/{}_short_bars.txt'.format(symbol)).st_size != 0 and os.stat('data/bars/{}_long_bars.txt'.format(symbol)).st_size != 0:
                        print(symbol)  
                        df = pd.read_csv('data/bars/{}_short_bars.txt'.format(symbol), parse_dates=True, index_col='Date')
                        df2 = pd.read_csv('data/bars/{}_long_bars.txt'.format(symbol), parse_dates=True, index_col='Date')
                        close_list = df['Close'].tolist()
                        long_close_list = df2['Close'].tolist()

                        if len(close_list) >= 3 and len(long_close_list) >=1:
                            ordered_to_buy_security = False
                            orders_data = config.get_orders('open', 1, symbol, 'buy', 'desc')
                            if orders_data:
                                ordered_to_buy_security = True
                            else:
                                ordered_to_buy_security = False
                            
                            ordered_to_sell_security = False
                            orders_data = config.get_orders('open', 1, symbol, 'sell', 'desc')
                            if orders_data:
                                ordered_to_sell_security = True
                            else:
                                ordered_to_sell_security = False
                                
                            own_security = False
                            positions_data = config.get_positions(symbol)
                            if 'code' not in positions_data:
                                    own_security = True
                            else:
                                own_security = False

                            ordered_to_stop_security = False
                            orders_data = config.get_orders('open', 1, symbol, 'sell', 'desc')
                            try:
                                if orders_data[0]['type'] == 'stop':
                                    ordered_to_stop_security = True
                            except:
                                ordered_to_stop_security =  False
                            finally:
                                ordered_to_stop_security = False


                            high_list = df['High'].tolist()
                            low_list = df['Low'].tolist()
                            long_high_list = df2['High'].tolist()
                            long_low_list = df2['Low'].tolist()
                            pivotpoints = []
                            support1points = []
                            support2points = []
                            support3points = []
                            resistance1points = []
                            resistance2points = []
                            resistance3points = []

                            print(len(long_close_list))

                            for i in range(len(long_close_list)):
                                pivotpoint = (long_high_list[i] + long_low_list[i] + long_close_list[i])/3
                                pivotpoints.append(pivotpoint)
                                support1 = pivotpoint - (long_high_list[i]- pivotpoint)
                                support1points.append(support1)
                                support2 = pivotpoint -(long_high_list[i]-long_low_list[i])
                                support2points.append(support2)
                                support3 = support1 - (long_high_list[i]-long_low_list[i])
                                support3points.append(support3)
                                resistance1 = pivotpoint + (pivotpoint-long_low_list[i])
                                resistance1points.append(resistance1)
                                resistance2 = pivotpoint + (long_high_list[i]-long_low_list[i])
                                resistance2points.append(resistance2)
                                resistance3 = resistance1 + (long_high_list[i] - long_low_list[i])
                                resistance3points.append(resistance3)

                            points = [pivotpoints[-1], support1points[-1], support2points[-1], support3points[-1], resistance1points[-1], resistance2points[-1], resistance3points[-1]]
                            greater_points = []
                            lesser_points = []

                            for point in points:
                                if point >= close_list[-1]:
                                    greater_points.append(point)
                                if point <= close_list[-1]:
                                    lesser_points.append(point)
                            
                            if len(greater_points)>0 and len(lesser_points)>0:
                                resistance_break_point = min(greater_points)
                                support_break_point = max(lesser_points)
                            else:
                                resistance_break_point = close_list[-1]
                                support_break_point = close_list[-1]

                            for point in points:
                                if point == close_list[-1]:
                                    resistance_break_point = close_list[-1]
                                    support_break_point = close_list[-1]


                            portfolio_history = config.get_portfolio_history('1D', short_timeframe_string)
                            for i in range(len(portfolio_history['equity'])):
                                if portfolio_history['equity'][i] == portfolio_history['equity'][-1]:
                                    equity = portfolio_history['equity'][i]
                                    break
                                elif portfolio_history['equity'][i+1] == None:
                                    equity = portfolio_history['equity'][i]
                                    break
                            risk = close_list[-1] - support_break_point
                            if risk <= equity/100:
                                position_qty = round((equity/100)/close_list[-1])
                            elif position_qty * close_list[-1] > equity/100:
                                position_qty -= 1
                            else:
                                position_qty = 0
                            
                            if close_list[-1] < resistance_break_point and close_list[-2] >= resistance_break_point and own_security == True and ordered_to_buy_security == False:
                                config.close_position(symbol)
                            if close_list[-1] > support_break_point and close_list[-2] <= support_break_point and own_security == False and ordered_to_buy_security == False:
                                if ordered_to_sell_security == True:
                                    order_data = config.get_orders('open', 1, symbol, 'sell', 'desc')
                                    print(config.cancel_order(order_data[0]['id']))
                                print(config.create_side_order(symbol, position_qty, 'buy', 'market', 'day'))
                                if ordered_to_stop_security == False:
                                    print(config.create_stop_order(symbol, position_qty, 'sell', 'stop', 'day', (round(support_break_point,2))))
                            
                            

