

class RealType(object):



    MIN_UNIT = {
           "BTCUSDT": 0.01,
           "ETHUSDT": 0.01,
           "BNBUSDT": 0.0001
       },

    MIN_UNIT_POS = {
                       "BTCUSDT": 2,
                       "ETHUSDT": 2,
                       "BNBUSDT": 4
                   },

    AMOUNT_UNIT = {
                      "BTCUSDT": 6,
                      "ETHUSDT": 5,
                      "BNBUSDT": 2
                  },

    ORDER = {
        "SIDE":{
            'bid':'BUY',
            'ask':'SELL'
        },

        'ORDTYPE':{
            'limit':'LIMIT',
            'price':'MARKET',
            'market':'MARKET',
            'stop_loss_limit':'STOP_LOSS_LIMIT'
        },

        # min price movement
        'MPM' :{
            'BTCUSDT': 0.01,
            'ETHUSDT': 0.01,
            'BNBUSDT': 0.0001
        },

        # min trade amount
        'MTA' : {
            'BTCUSDT': 0.000001,
            'ETHUSDT': 0.00001,
            'BNBUSDT': 0.01
        }
    }

    LAST_EMPTY = {

    }
