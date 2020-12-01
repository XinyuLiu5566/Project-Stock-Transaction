import urllib.request
import json
import urllib
import pandas as pd
#import matplotlib.pyplot as plt
from datetime import date
import time
import numpy as np
from django.db import connection


def check_macd(df,judge):
    close_price=df['close']
    d=pd.DataFrame(close_price)
    data=d
    #大于60日均线
    #if ma['ma60'][0]>float(d['close'][-1:]):
     #   return False
    #量比
    short_=12
    long_=26
    m=9
    data['diff']=data['close'].ewm(adjust=False,alpha=2/(short_+1),ignore_na=True).mean()-\
                data['close'].ewm(adjust=False,alpha=2/(long_+1),ignore_na=True).mean()
    data['dea']=data['diff'].ewm(adjust=False,alpha=2/(m+1),ignore_na=True).mean()
    data['macd']=2*(data['diff']-data['dea'])
    yellow=data['dea']
    black=data['diff']
    macd=list(data.macd)
    #出现金叉
    if macd[-1]>0 and (macd[-2]<0):
        #出现反复横跳
        #if macd[-3]*macd[-4]<0 or macd[-3]*macd[-5]<0 or macd[-4]*macd[-5]<0:
        macd=list(data.macd[-30:])
        for i,j in enumerate(macd):
            if j < 0:
                for a,b in enumerate(macd[i+1:]):
                    if b>0:
                        for c,d in enumerate(macd[i+1:][a+1:]):
                            if d<0:
                                for e,f in enumerate(macd[i+1:][a+1:][c+1:]):
                                    if f>0:
                                        judge=True
    return judge
def check_kdj(df):
    #kdj
    df['rolling_high'] = df['high'].rolling(window = 9, min_periods = 1).max()
    df['rolling_low'] = df['low'].rolling(window = 9, min_periods = 1).min()
    df['fastk'] = (df['close'] - df['rolling_low']) / (df['rolling_high'] - df['rolling_low']) * 100
    df['fastd'] = df['fastk'].ewm(com = 2, adjust = False).mean()
    df['K'] = df['fastd']
    df['D'] = df['K'].ewm(com = 2, adjust = False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    df['kdj'] = ''
    kdj_position=df['K']>df['D']
    df.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'kdj'] = '金叉'
    df.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'kdj'] = '死叉'
    if list(df.J)[-1]>80:
        return False
    if list(df.J)[-1] <20 and list(df.J)[-2] <20 and list(df.J)[-3] <20:
        if list(df.D)[-1] <20 and list(df.D)[-2] <20 and list(df.D)[-3] <20:
            if list(df.K)[-1] <20 and list(df.K)[-2] <20 and list(df.K)[-3] <20 :
                return True
    if list(df.kdj)[-1]=='金叉':
        if '死叉' in list(df.kdj)[-6:-1]:
            return True
    return True
def check_boll(df):
    df['mid']=df['close'].rolling(26).mean()
    df['tmp2']=df['close'].rolling(20).std()
    df['top']=df['mid']+2*df['tmp2']
    df['bottom']=df['mid']-2*df['tmp2']
    if list(df.close)[-1]>list(df.top)[-1]:
        return False
    if list(df.close)[-1]<list(df.bottom)[-1]:
        return True
    if not (list(df.top)[-2]<list(df.top)[-1] and list(df.bottom)[-2]>list(df.bottom)[-1]):
        return False
    return True
def RSI(array_list, periods=7):
    length = len(array_list)
    rsies = [np.nan] * length
    if length <= periods:
        return rsies
    up_avg = 0
    down_avg = 0

    first_t = array_list[:periods + 1]
    for i in range(1, len(first_t)):
        if first_t[i] >= first_t[i - 1]:
            up_avg += first_t[i] - first_t[i - 1]
        else:
            down_avg += first_t[i - 1] - first_t[i]
    up_avg = up_avg / periods
    down_avg = down_avg / periods
    rs = up_avg / down_avg
    rsies[periods] = 100 - 100 / (1 + rs)

    for j in range(periods + 1, length):
        up = 0
        down = 0
        if array_list[j] >= array_list[j - 1]:
            up = array_list[j] - array_list[j - 1]
            down = 0
        else:
            up = 0
            down = array_list[j - 1] - array_list[j]
        up_avg = (up_avg * (periods - 1) + up) / periods
        down_avg = (down_avg * (periods - 1) + down) / periods
        rs = up_avg / down_avg
        rsies[j] = 100 - 100 / (1 + rs)
    return rsies

def predict(day):
    good_stock_macd=[]
    good_stock_boll=[]
    good_stock_kdj=[]
    good_stock=[]
    good_stock_turnover=[]
    good_stock_rsi=[]
    count=0
    cursor = connection.cursor()
    query = "SELECT ts_code FROM stock_info"
    cursor.execute(query)
    stock_list = cursor.fetchall()

    for j,i in enumerate(stock_list):
        count=count+1
        if count==200:
            count=0
            time.sleep(30)
        
        query = "SELECT * FROM daily_info WHERE ts_code = '"+i[0]+"' and trade_date < '"+str(day)+"' Order by trade_date"
        cursor.execute(query)
        df = cursor.fetchall()
        df = pd.DataFrame(list(df), columns = ['ts_code','trade_date','open','high','low','close','pre_close','change','pct_chg','vol','amount'])
        # df = df.reset_index(drop = True) 
        # df = pro.daily(ts_code=i, start_date='20190817', end_date=day)
        #df[5] = df['close']
        if len(df)>10 and df['close'][0]>1:
            judge=False
            try:
                df=df.iloc[::-1].reset_index(drop=True)
                if check_macd(df,judge):
                    good_stock.append(str(i[0]))
            except Exception as e:
                print('error')
                pass

    cursor1 = connection.cursor()
    for i in good_stock:
        query = "SELECT * FROM daily_info WHERE ts_code = '"+str(i)+"' and trade_date < '"+str(day)+"' Order by trade_date"
        cursor1.execute(query)
        df = cursor1.fetchall()
        df = pd.DataFrame(list(df), columns = ['ts_code','trade_date','open','high','low','close','pre_close','change','pct_chg','vol','amount'])
        # df = df.reset_index(drop = True)  
        df=df.iloc[::-1].reset_index(drop=True)
        if check_kdj(df):
            good_stock_macd.append(i)

    cursor2 = connection.cursor()
    for i in good_stock_macd:
        cursor2 = connection.cursor()
        query = "SELECT * FROM daily_info WHERE ts_code = '"+str(i)+"' and trade_date < '"+str(day)+"' Order by trade_date"
        cursor2.execute(query)
        df = cursor2.fetchall()
        df = pd.DataFrame(list(df), columns = ['ts_code','trade_date','open','high','low','close','pre_close','change','pct_chg','vol','amount'])
        # df = df.reset_index(drop = True)  
        df=df.iloc[::-1].reset_index(drop=True)
        if RSI(df['close'])[-1]<75:
            good_stock_rsi.append(i)
    return good_stock_rsi

