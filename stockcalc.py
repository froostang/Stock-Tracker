import csv
from googlefinance import getQuotes
import json
import time
import arrow
import datetime

tl1 = "cl2.csv"
tl2 = "cl1.csv"

tickers = []
tickersTwo = []

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

with open(tl1, newline='') as csvfile, open(tl2, newline='') as csvfileTwo:
    fOne = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(fOne)
    for row in fOne:
        temp = row[0].replace(" ","")
        tickers.append(temp.replace("\"",""))
    fTwo = csv.reader(csvfileTwo, delimiter=',', quotechar='|')
    next(fTwo)
    for row in fTwo:
        temp = row[0].replace(" ","")
        tickersTwo.append(temp.replace("\"",""))

ml = tickers+tickersTwo
no = 0

rotNum = 0
preValues = {}
hotness = {}

fullCycle = {
    'rot0':[],
    'rot1':[],
    'rot2':[],
    'rot3':[],
}

# loops and gets the first 4 batches (100, 100, 100, remainder)
while True:
    for x in batch(ml, 100):
        quoteChunk = getQuotes(x)
        __rotNo = "rot" + str(no)
        quoteChunk[0]['mystamp'] = datetime.datetime.now()
        fullCycle[__rotNo]=fullCycle[__rotNo]+quoteChunk
        
    no = no + 1
    if ( no == 4 ):
        #calculate acceleration and dump accelerators to db
        _d = datetime.datetime.now()
        t1,t2,t3,t4 = _d,_d,_d,_d
        for i in range(0, len(fullCycle['rot0'])):
            if (not fullCycle['rot0'][i]['LastTradePrice']):
                y1 = 0
            else:
                y1 = float(fullCycle['rot0'][i]['LastTradePrice'])
            if (not fullCycle['rot1'][i]['LastTradePrice']):
                y2 = 0
            else:
                y2 = float(fullCycle['rot1'][i]['LastTradePrice'])
            if (not fullCycle['rot2'][i]['LastTradePrice']):
                y3 = 0
            else:
                y3 = float(fullCycle['rot2'][i]['LastTradePrice'])
            if (not fullCycle['rot3'][i]['LastTradePrice']):
                y4 = 0
            else: 
                y4 = float(fullCycle['rot3'][i]['LastTradePrice'])

            if ( 'mystamp' in fullCycle['rot0'][i] ):
                t1 = fullCycle['rot0'][i]['mystamp']
            if ( 'mystamp' in fullCycle['rot1'][i] ):
                t2 = fullCycle['rot1'][i]['mystamp']
            if ( 'mystamp' in fullCycle['rot2'][i] ):
                t3 = fullCycle['rot2'][i]['mystamp']
            if ( 'mystamp' in fullCycle['rot3'][i] ):
                t4 = fullCycle['rot3'][i]['mystamp']
            
            v1t = (t2-t1).total_seconds()
            v1 = (y2-y1) / v1t

            v2t = (t4-t3).total_seconds()
            v2 = (y4-y3) / v2t

            a1 = (v2 - v1) / ( v2t - v1t )

            fullCycle['rot3'][i]['accelerationVal'] = a1

        for e in fullCycle['rot3']:
            a = e['accelerationVal']
            if a != 0.0 and a> 0.1:
                # checks to see for 3 continuous rotations of acceleration > 0.1 and adds them to list hotness
                if ((preValues[e['StockSymbol'][rotNum - 1]] > 0) and (preValues[e['StockSymbol'][rotNum - 2]] > 0)):
                    hotness['StockSymbol'] = a, preValues[e['StockSymbol'][rotNum - 1]], preValues[e['StockSymbol'][rotNum - 2]] 
                else :
                    preValues[e['StockSymbol']][rotNum] = a
                if(hotness):
                    print(hotness)
                else :
                    print("nothing yet....")
                # print( e['StockSymbol'] )
                # print( e['accelerationVal'] )

        fullCycle['rot0'] = []
        fullCycle['rot1'] = []
        fullCycle['rot2'] = []
        fullCycle['rot3'] = []
        no = 0
        rotNum = rotNum + 1
