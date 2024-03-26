import pandas as pd, requests, datetime

class Security:
    
    def __init__(self, symbol, api_key, secret_key):
        self.symbol = symbol
        self.headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
        }
        self.market_data_api_url = 'https://data.alpaca.markets/v2'
        self.trading_api_url = 'https://paper-api.alpaca.markets/v2'
        self.analysable = True
        self.get_minute_bars()
        self.get_day_bars()
        self.get_time()
        

    def sold(self):
        orders_data = self.get_orders('open', 'sell', 'desc')
        if orders_data:
            return True
        else:
            return False

    def bought(self):
        orders_data = self.get_orders('open', 'buy', 'desc')
        if orders_data:
            return True
        else:
            return False

    def owned(self):
        positions_data = self.get_positions()
        if 'code' not in positions_data:
            return True
        else:
            return False

    def stopped(self):
        orders_data = self.get_orders('open', 'sell', 'desc')
        try:
            if orders_data[0]['type'] == 'stop':
                return True
        except:
            return False
        finally:
            return False

    def get_minute_bars(self, limit=10000):
        previous_date = datetime.datetime.today() - datetime.timedelta(days=2) 
        start = str(previous_date)[:10] + 'T14:30:00Z'
        r = requests.get(self.market_data_api_url + '/stocks/{}/bars?timeframe={}&start={}&limit={}'.format(self.symbol,'1Min',start,limit), headers= self.headers)
        bars = r.json()
        print(bars)
        if bool(bars['bars']) == False:
            self.analysable = False
        if self.analysable == True:
            self.minute_bars = pd.DataFrame({'Date':[],'Open':[],'High':[],'Low':[],'Close':[],'Volume':[],'OpenInterest':[]})
            for bar in bars['bars']:
                self.minute_bars.loc[len(self.minute_bars.index)]=[bar['t'],bar['o'],bar['h'],bar['l'],bar['c'],bar['v'], 0.00]
            if len(self.minute_bars.index) >=2:
                self.latest_minute_bar_close = self.minute_bars['Close'][len(self.minute_bars.index)-1]
                self.previous_minute_bar_close = self.minute_bars['Close'][len(self.minute_bars.index)-2]
                self.latest_minute_bar_high = self.minute_bars['High'][len(self.minute_bars.index)-1]
                self.previous_minute_bar_high = self.minute_bars['High'][len(self.minute_bars.index)-2]
                self.latest_minute_bar_low = self.minute_bars['Low'][len(self.minute_bars.index)-1]
                self.previous_minute_bar_low = self.minute_bars['Low'][len(self.minute_bars.index)-2]
                self.latest_minute_bar_open = self.minute_bars['Open'][len(self.minute_bars.index)-1]
                self.previous_minute_bar_open = self.minute_bars['Open'][len(self.minute_bars.index)-2]
            else:
                self.analysable = False
    
    def get_day_bars(self,  limit=10000,):
        previous_date = datetime.datetime.today() - datetime.timedelta(days=2) 
        start = str(previous_date)[:10] + 'T14:30:00Z'
        r = requests.get(self.market_data_api_url + '/stocks/{}/bars?timeframe={}&start={}&limit={}'.format(self.symbol,'1Day' ,start,limit), headers= self.headers)
        bars = r.json()
        if bool(bars['bars']) == False:
            self.analysable = False
        if self.analysable == True:
            self.day_bars = pd.DataFrame({'Date':[],'Open':[],'High':[],'Low':[],'Close':[],'Volume':[],'OpenInterest':[]})
            for bar in bars['bars']:
                self.day_bars.loc[len(self.day_bars.index)]=[bar['t'],bar['o'],bar['h'],bar['l'],bar['c'],bar['v'], 0.00]
            if len(self.day_bars.index) >=2:
                self.latest_day_bar_close = self.day_bars['Close'][len(self.day_bars.index)-1]
                self.previous_day_bar_close = self.day_bars['Close'][len(self.day_bars.index)-2]
                self.latest_day_bar_high = self.day_bars['High'][len(self.day_bars.index)-1]
                self.previous_day_bar_high = self.day_bars['High'][len(self.day_bars.index)-2]
                self.latest_day_bar_low = self.day_bars['Low'][len(self.day_bars.index)-1]
                self.previous_day_bar_low = self.day_bars['Low'][len(self.day_bars.index)-2]
                self.latest_day_bar_open = self.day_bars['Open'][len(self.day_bars.index)-1]
                self.previous_day_bar_open = self.day_bars['Open'][len(self.day_bars.index)-2]
            else:
                self.analysable = False

    def get_time(self):
        self.sell_at_day_end = False
        now = datetime.datetime.utcnow()
        time_in_seconds = (now.hour*60*60)+(now.minute*60)+(now.second)
        week_day = datetime.datetime.today().weekday()
        if time_in_seconds < 52200 or time_in_seconds > 75400 or week_day >= 5:
            self.analysable = False
        if time_in_seconds > 75400 and time_in_seconds < 75600 and week_day < 5:
            self.sell_at_day_end = True

    def get_pivot_points(self):
        if self.analysable == True:
            self.pivotpoint = (self.previous_day_bar_high + self.previous_day_bar_low + self.previous_day_bar_close)/3
            self.support1 = self.pivotpoint - (self.previous_day_bar_high- self.pivotpoint)
            self.support2 = self.pivotpoint -(self.previous_day_bar_high-self.previous_day_bar_low)
            self.support3 = self.support1 - (self.previous_day_bar_high-self.previous_day_bar_low)
            self.resistance1 = self.pivotpoint + (self.pivotpoint-self.previous_day_bar_low)
            self.resistance2 = self.pivotpoint + (self.previous_day_bar_high-self.previous_day_bar_low)
            self.resistance3 = self.resistance1 + (self.previous_day_bar_high - self.previous_day_bar_low)

            self.points = [self.pivotpoint, self.support1, self.support2, self.support3, self.resistance1, self.resistance2, self.resistance3]
            greater_points = []
            lesser_points = []

            for point in self.points:
                if point >= self.latest_minute_bar_close:
                    greater_points.append(point)
                if point <= self.latest_minute_bar_close:
                    lesser_points.append(point)
                                
            if len(greater_points)>0 and len(lesser_points)>0:
                self.resistance_break_point = min(greater_points)
                self.support_break_point = max(lesser_points)
            else:
                self.analysable = False

            for point in self.points:
                if point == self.latest_minute_bar_close:
                    self.analysable = False

    def get_orders(self, status, side, direction, limit=1):
        r = requests.get(self.trading_api_url + '/orders?status={}&limit={}&symbols={}&side={}&direction={}'.format(status,limit,self.symbol,side,direction), headers= self.headers)
        return r.json()

    def get_positions(self):
        r = requests.get(self.trading_api_url + '/positions/{}'.format(self.symbol), headers= self.headers)
        return r.json()

    def get_position_qty(self,potential_risk=0, period='1D', timeframe='1Min'):
        if self.analysable == True:
            r = requests.get(self.trading_api_url + '/account/portfolio/history?period={}&timeframe={}'.format(period,timeframe), headers= self.headers)
            portfolio_history = r.json()
            for i in range(len(portfolio_history['equity'])):
                if portfolio_history['equity'][i] == portfolio_history['equity'][-1]:
                    self.equity = portfolio_history['equity'][i]
                    break
                elif portfolio_history['equity'][i+1] == None:
                    self.equity = portfolio_history['equity'][i]
                    break
            risk = self.latest_minute_bar_close - potential_risk
            if risk <= self.equity/100:
                self.position_qty = round((self.equity/100)/self.latest_minute_bar_close)
            elif self.position_qty * self.latest_minute_bar_close > self.equity/100:
                self.position_qty -= 1
            else:
                self.position_qty = 0

    def create_side_order(self, qty, side, type, time_in_force):
            data = {
                'symbol': self.symbol,
                'qty': qty,
                'side': side,
                'type': type,
                'time_in_force': time_in_force,

            }
            r = requests.post(self.trading_api_url + '/orders', json=data, headers = self.headers)
            return r.json()

    def create_stop_order(self ,qty, side, type, time_in_force, stop_price):
        data = {
                'symbol': self.symbol,
                'qty': qty ,
                'side': side,
                'type': type,
                'time_in_force': time_in_force,
                'stop_price': stop_price,
            }
        r = requests.post(self.trading_api_url + '/orders', json=data, headers = self.headers)
        return r.json()

    def cancel_order(self, status, side, direction):
        order_data = self.get_orders(status, side, direction)
        order_id = order_data[0]['id']
        requests.delete(self.trading_api_url + '/orders/{}'.format(order_id), headers = self.headers)

    def close_position(self):
        r = requests.delete(self.trading_api_url + '/positions/{}'.format(self.symbol), headers= self.headers)
        return r.json()

    

