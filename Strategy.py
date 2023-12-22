import pandas_ta as ta
from NorenRestApiPy.NorenApi import  NorenApi
import pandas as pd
import time
import pyotp
import math
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

#Discord authentication
url='https://discord.com/api/v9/channels/1091057642513907792/messages'
auth={
    'authorization':'ODM5MTQyNDY4MDY1Njg5Njgy.G3aeA6.95EgLoGiFSpXn4Lvb8uISzNamiID9jvGVlOYBE',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}



#Gspread authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('F:\Algo USDINR\ShoonyaApi-py-master\ShoonyaApi-py-master\shoonya-api-9c9797820ce7.json', scope)
sheet_name = 'ShoonyaApi Trades'
client = gspread.authorize(creds)
sheet = client.open('ShoonyaApi Trades')
worksheet= sheet.worksheet('Sheet1')


#ShoonyaApi
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        global api
        api = self



api = ShoonyaApiPy()
token = 'PAJ46A35K6SNEB53J4U43IX522X33CP5'
otp = pyotp.TOTP(token).now()
user        = 'FA56947'
pwd       = 'Algo@1652'
factor2     = otp
vc          = 'FA56947_U'
app_key     = 'b1b10ff51c7f8c21b624e5e39e94b55d'
imei        = 'abc1234' 
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
print(ret['stat'])





info=api.get_limits()
print(info)
i=2
order=0


#converter from numpy to float

def float64 (a):
    val = np.float64(a)
    pyval = val.item()
    return pyval 

def float32 (a):
    val = np.float32(a)
    pyval = val.item()
    return pyval


def get_time_series(exchange, token, days, interval):
    # Get the current date and time
    now = datetime.now()

    # Set the time to midnight
    now = now.replace(hour=9, minute=0, second=0, microsecond=0)

    # Subtract days
    prev_day = now - timedelta(days=days)

    # Get the timestamp for the previous day
    prev_day_timestamp = prev_day.timestamp()

    # Use the prev_day_timestamp in your api call
    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=prev_day_timestamp, interval=interval)
    if ret:
        return pd.DataFrame(ret)
    else:
        print("No Data for the given exchange, token, days and interval")

#current time
def get_current_time():
        current_time = datetime.now()
        time_str = current_time.strftime('%H%M%S')
        return int(time_str)

while i>1:

    time.sleep(5)
    
        
    current_time = get_current_time()
    print(current_time)
    


    #Calculating SuperTrend

    def supertrend(exchange, token, days, interval, ATR, Multi):
        # Get the time series data
        df = get_time_series(exchange, token, days, interval)
        df = df.sort_index(ascending=False)
        df[['into','intl','intc','inth']] = df[['into','intl','intc','inth']].apply(pd.to_numeric)
        #df[['into','intl','intc','inth']]
        sti = ta.supertrend(df['inth'], df['intl'], df['intc'], length=ATR, multiplier=Multi)
        sti = sti.sort_index(ascending=True)
        
        
        sti['super_trend'] = sti[['SUPERT_20_2.0']]
        result = pd.concat([df, sti], axis=1)
        results = result.sort_index(ascending=True).rename(columns={'SUPERTd_20_2.0': 'signal', 'SUPERTl_20_2.0': 'S_UPT','SUPERTs_20_2.0': 'S_DT'})
        results[['into','inth','intl','intc','SUPERT_20_2.0','signal']]=results[['into','inth','intl','intc','SUPERT_20_2.0','signal']].apply(pd.to_numeric)
        return results[['time','into','inth','intl','intc','signal','SUPERT_20_2.0','S_UPT','S_DT']]


    
    df = supertrend('CDS', '3637', 4, 10, 20, 2)
    df = df.set_index('time')
    df = df.sort_index(ascending=True)

    # LTP = current price

    
    


    #data sorting and close data of every 10min interval candle

    data = get_time_series('CDS',"3637",4,10)
    data= data.rename(columns={'intc':'close' , 'into':'open' , 'inth':'high' , 'intl':'low'})
    data = data.set_index('time')
    data = data.sort_index(ascending=True)




    #Calculate SMA20 
    sma20 = data.ta.sma(20).dropna()

    
    

    #Organising Previous Candle Data into relevent variables

    sig=df["signal"].iloc[-2]
    sig=float32(sig)
    

    op=data["open"].iloc[-2]
    op=float64(op)
    
    
    high=data["high"].iloc[-2]
    high=float64(high)
    

    low=data["low"].iloc[-2]
    low=float64(low)
    

    close=data["close"].iloc[-2]
    close=float64(close)

    
    

    # sclose = df["intc"].iloc[-2]
    # sclose=float64(sclose)


    sma20v=sma20.iloc[-2]
    sma20v=float64(sma20v)
    

    Candle_Size= high-low


    LPi=api.get_quotes('CDS', '3637')
    lp=LPi['lp']
    LTP=float(lp)
    
    

    
    
    q=3
    # q=100/round((Candle_Size*1000),4)
    #quantity 

    #LONG TP AND SL 

    Buy_tp= round(high+(Candle_Size*2),4)
    Buy_Sl = low-0.0025


    #SHORT TP AND SL 

    Sell_tp= round(low-(Candle_Size*2),4)
    Sell_Sl= high+0.0025  


 #Entry and Exit conditions

    if 100000 < get_current_time() < 153000:


     #BB Break Strategy


        #Buy
        # if sclose>



     #Retracement Strategy


        #Buy
        if sig==1 and low<=sma20v and op>=sma20v and close>=sma20v and high<=LTP :

            Buy_order=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='CDS', tradingsymbol='USDINR26APR23F', 
                        quantity=q, discloseqty=0,price_type='LMT', price=high+0.0025, trigger_price=0,
                        retention='DAY', remarks='Long')
            
            BTP_order=api.place_order(buy_or_sell='S', product_type='I',
                        exchange='CDS', tradingsymbol='USDINR26APR23F', 
                        quantity=q, discloseqty=0,price_type='LMT', price=Buy_tp, trigger_price=0,
                        retention='DAY', remarks='BTP')
            
            BSL_order=api.place_order(buy_or_sell='S', product_type='I',
                        exchange='CDS', tradingsymbol='USDINR26APR23F', 
                        quantity=q, discloseqty=0,price_type='SL-LMT', price=Buy_Sl, trigger_price=Buy_Sl,
                        retention='DAY', remarks='BSL')
            order=1
            tp = Buy_tp
            sl= Buy_Sl
            break

        #Sell
        elif sig==(-1) and high>=sma20v and op<=sma20v and close<=sma20v and low>=LTP:

            Sell_order=api.place_order(buy_or_sell='S', product_type='I',
                        exchange='CDS', tradingsymbol='USDINR26APR23F', 
                        quantity=q, discloseqty=0,price_type='LMT', price=low-0.0025, trigger_price=0,
                        retention='DAY', remarks='Short')
            
            STP_order=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='CDS', tradingsymbol='USDINR26APR23F', 
                        quantity=q, discloseqty=0,price_type='LMT', price=Sell_tp, trigger_price=0,
                        retention='DAY', remarks='STP')
            
            SSL_order=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='CDS', tradingsymbol='USDINR26APR23F', 
                        quantity=q, discloseqty=0,price_type='SL-LMT', price=Sell_Sl, trigger_price=high,
                        retention='DAY', remarks='SSL')
            order=2
            tp = Sell_tp
            sl= Sell_Sl
            break

# if(order==1):
#     while i>1:
#         time.sleep(20)
#         print(get_current_time())
#         if(BTP_order[0]['norenordno'])







    


#Order Details
ret = api.get_trade_book()
print('TRADE taken, Check google sheet')
date=ret[0]['norentm']
remarks=ret[0]['remarks']
qty=ret[0]['fillshares']
price=ret[0]['flprc']
stoploss=sl
sl=str(sl)
target=tp
tp=str(tp)



#Google Sheet update
worksheet.insert_row([date,remarks,qty,price,stoploss,target],2)

#Discord notification
msg={
    'content': date+'\n'+remarks+'\n'+qty+'\n'+price+'\n'+sl+'\n'+tp
}
try:
    requests.post(url,headers=auth,data=msg)
except:
    print('discord error')

# if order==2:
#     print(STP_order)
#     print(SSL_order)
# elif order==1:
#     print(BTP_order)
#     print(BSL_order)

api.logout()



