import requests

API_KEY ='Your API key here'
SECRET_KEY ='Your secret key here'
HEADERS = {
    'APCA-API-KEY-ID':API_KEY,
    'APCA-API-SECRET-KEY': SECRET_KEY
}
MARKET_DATA_API_URL = 'https://data.alpaca.markets/v2'
TRADING_API_URL = 'https://paper-api.alpaca.markets/v2'
BROKER_API_URL = 'https://broker-api.alpaca.markets/v2'
MINUTE_BARS_URL = MARKET_DATA_API_URL + '/stocks/bars'
ORDERS_URL = TRADING_API_URL + '/orders'
ACCOUNT_URL = TRADING_API_URL + '/account'
POSITIONS_URL = TRADING_API_URL + '/positions'
PORTFOLIO_HISTORY_URL = TRADING_API_URL + '/account/portfolio/history'

def get_portfolio_history(period, timeframe):
    r = requests.get(PORTFOLIO_HISTORY_URL + '?period={}&timeframe={}'.format(period,timeframe), headers= HEADERS)
    return r.json()

def get_bars(symbols, timeframe, limit):
    r = requests.get(MINUTE_BARS_URL + '?symbols={}&timeframe={}&limit={}'.format(symbols,timeframe,limit), headers= HEADERS)
    return r.json()

def get_orders(status, limit, symbols, side, direction):
    r = requests.get(ORDERS_URL + '?status={}&limit={}&symbols={}&side={}&direction={}'.format(status,limit,symbols,side,direction), headers= HEADERS)
    return r.json()

def get_positions(symbol):
    r = requests.get(POSITIONS_URL + '/{}'.format(symbol), headers= HEADERS)
    return r.json()

def create_side_order(symbol, qty, side, type, time_in_force):
        data = {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,

        }
        r = requests.post(ORDERS_URL, json=data, headers = HEADERS)
        return r.json()

def create_stop_order(symbol, qty, side, type, time_in_force, stop_price):
    data = {
            'symbol': symbol,
            'qty': qty ,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
            'stop_price': stop_price,
        }
    r = requests.post(ORDERS_URL, json=data, headers = HEADERS)
    return r.json()

def cancel_order(order_id):
    r = requests.delete(ORDERS_URL + '/{}'.format(order_id), headers = HEADERS)

def cancel_all_orders():
    r = requests.delete(ORDERS_URL, headers = HEADERS)
    return r.json()

def close_position(symbol):
    r = requests.delete(POSITIONS_URL + '/{}'.format(symbol), headers= HEADERS)
    return r.json()

def close_all_positions():
    r = requests.delete(POSITIONS_URL, headers= HEADERS)
    return r.json()


