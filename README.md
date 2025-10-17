# BTC Order Book Aggregator

Simple Python script that fetches Bitcoin prices from Coinbase and Gemini exchanges and calculates execution costs.

## Setup
pip install requests

## Usage
# Buy/sell 10 BTC (default)
python orderbook.py

# Custom quantity
python order_book.py --qty 5

## How I Built This

### 1. API Discovery
- First called Coinbase API and printed the response
- Saw it returns arrays like `[["95000.50", "0.5"], ...]`
- Then tried Gemini - different format! Uses objects like `{"price": "95000", "amount": "0.5"}`
- Had to write separate parsers for each exchange

### 2. Main Challenges
- **Sorting**: Confused me at first - needed to sort by price only using `key=lambda x: x[0]`, not the whole list
- **Gemini format**: Uses "amount" while Coinbase uses "size" - spent time figuring this out
- **Rate limiting**: Used a closure with a cache dictionary to avoid hitting APIs too fast
- **Error handling**: Added try/except when I realized APIs can fail or timeout

### 3. How It Works
1. Fetches order books from both exchanges (rate limited to once per 2 seconds)
2. Normalizes different data formats into `[[price, size], ...]` lists
3. Merges order books and sorts by price
4. Walks through prices to calculate buy/sell costs

## Assumptions
- Both exchanges might not always be available (added error handling)
- Using level 2 order book (not full market depth)
- Prices displayed with 2 decimal places

## Output Example
```
Fetching order books for 10 BTC...

Best bid: $95,234.50 (size: 2.5 BTC)
Best ask: $95,456.00 (size: 1.8 BTC)

To buy 10 BTC: $954,567.89
To sell 10 BTC: $952,345.67
```