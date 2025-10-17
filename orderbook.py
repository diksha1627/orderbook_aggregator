import requests
import time
import argparse

def fetch_coinbase_data():
    url = "https://api.exchange.coinbase.com/products/BTC-USD/book?level=2"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        # print(data,"data valuee")
        return data
    except Exception as e:
        print(f"Error fetching Coinbase: {e}")
        return None
    
    
def fetch_gemini_data():
    url = "https://api.gemini.com/v1/book/BTCUSD"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data
    except Exception as e:
        print(f"Error fetching Gemini: {e}")
        return None
    
    
def normalizing_coinbase(data):
    if data is None or 'bids' not in data:
        return [],[]
    
    bids = []
    asks = []
    
    for bid in data.get('bids', []):
        try:
            price = float(bid[0])
            size = float(bid[1])
            if price > 0 and size > 0:
                bids.append([price,size])
        except:
            continue
            
    for ask in data.get('asks', []):
        try:
            price = float(ask[0])
            size = float(ask[1])
            if price > 0 and size > 0:
                asks.append([price,size])
        except:
            continue
    
    # sorting by price by highest first for bids
    bids.sort(key=lambda x: x[0], reverse=True)
    
    # sorting by price by lowest first for asks
    asks.sort(key=lambda x: x[0])
    return bids , asks  

def normalizing_gemini(data):
    if data is None or 'bids' not in data:
        return [],[]
    
    bids = []
    asks = []
    
    # gemini normalization
    for bid in data.get('bids', []):
        try:
            price = float(bid.get('price', 0))
            size = float(bid.get('amount', 0))
            if price > 0 and size > 0:
                bids.append([price,size])
        except:
            continue
            
    for ask in data.get('asks', []):
        try:
            price = float(ask.get('price', 0))
            size = float(ask.get('amount', 0))
            if price > 0 and size > 0:
                asks.append([price,size])
        except:
            continue
    
    # sorting by price
    bids.sort(key=lambda x: x[0], reverse=True)
    asks.sort(key=lambda x: x[0])
    return bids , asks 

def buying_cost(asks,stocks):
    remStocks = stocks  
    total = 0 
    
    #  asks from lowest price
    for price,size in asks:
        if(remStocks <= 0):
           break
       
        toBuy = min(remStocks,size)
        total += toBuy * price
        remStocks = remStocks - toBuy
        
    if(remStocks > 0):
        print(f"Not enough liquidity to buy! Missing {remStocks} BTC")
         
    return total  

def selling_cost(bids,stocks):
    remStocks = stocks  
    total = 0 
    
    #  bids from highest price
    for price,size in bids:
        if(remStocks <= 0):
           break
       
        toSell = min(remStocks,size)
        total += toSell*price
        remStocks = remStocks - toSell
        
    if(remStocks > 0):
        print(f"Not enough buyers! Cant sell {remStocks} BTC")
         
    return total       

cache = {}
def rate_limiting(exch_name,fetch_func):
    currTime = time.time()
    
    if exch_name in cache:
        lastTime = cache[exch_name]['time']
        if currTime - lastTime < 2:
            print(f"Using cached data for {exch_name}")
            return cache[exch_name]['data']
    
    # calling actual function        
    data = fetch_func()
    cache[exch_name] = {
        'time':currTime,
        'data':data
    }
    return data

def mergeOrderBooks(coinbase_bids,coinbase_asks,gemini_bids,gemini_asks):
    # combine bids from both exchanges
    all_bids = coinbase_bids + gemini_bids
    all_bids.sort(key=lambda x: x[0], reverse = True)
    
    # combine asks from both exchanges
    all_asks = coinbase_asks + gemini_asks
    all_asks.sort(key=lambda x: x[0])
    
    return all_bids , all_asks

def format_price(amount):
    return f"${amount:,.2f}"  


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--qty',type=float,default=10)
    args = parser.parse_args()
    
    print(f"\nFetching order books for {args.qty} BTC...\n")
    
    # fetch with rate limiting
    coinbaseData = rate_limiting('coinbase', fetch_coinbase_data)
    geminiData = rate_limiting('gemini', fetch_gemini_data)
    
    # check if we got any data
    if not coinbaseData and not geminiData:
        print("No data from exchanges. Exiting.")
        return
    
    # normalize the data
    coinbase_bids , coinbase_asks  = normalizing_coinbase(coinbaseData) if coinbaseData else ([],[])
    gemini_bids , gemini_asks = normalizing_gemini(geminiData) if geminiData else ([],[])
    
    # merge books
    all_bids , all_asks  = mergeOrderBooks(coinbase_bids,coinbase_asks,gemini_bids,gemini_asks)
    
    # show best prices
    if all_bids:
        print(f"Best bid: ${all_bids[0][0]:,.2f} (size: {all_bids[0][1]} BTC)")
    if all_asks:
        print(f"Best ask: ${all_asks[0][0]:,.2f} (size: {all_asks[0][1]} BTC)")
    print()
    
    # calculate costs
    buying_cost_data = buying_cost(all_asks,args.qty)
    selling_cost_data = selling_cost(all_bids,args.qty)
    
    print(f"To buy {args.qty} BTC: {format_price(buying_cost_data)}")
    print(f"To sell {args.qty} BTC: {format_price(selling_cost_data)}")

if __name__ == "__main__":
    main()