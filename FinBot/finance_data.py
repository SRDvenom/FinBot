import yfinance as yf
import re

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)

        # Determine currency by exchange hint in ticker symbol
        currency = 'INR' if symbol.upper().endswith('.NS') else 'USD'

        # Try fast_info (works with newer yfinance versions)
        fast = getattr(stock, 'fast_info', None)
        if fast:
            # fast_info can be dict-like or object
            try:
                last = fast.get('last_price') if isinstance(fast, dict) else getattr(fast, 'last_price', None)
            except Exception:
                last = None
            if last:
                return float(last), currency

        # Fallback: try intraday data for today (more likely to be the latest close)
        data = stock.history(period="1d", interval="1m")
        if data is None or data.empty:
            # try a slightly larger window if 1d intraday empty
            data = stock.history(period="5d")
            if data is None or data.empty:
                return None

        price = float(data['Close'].iloc[-1])
        return price, currency
    except Exception:
        return None

def handle_stock_queries(message):
    msg = message.lower()
    match = re.search(r'price of ([a-zA-Z. ]+)', msg)

    if match:
        company_name = match.group(1).strip().upper()
        # Normalize map keys to uppercase so lookup matches the uppercased company_name
        stock_map = {
            "TCS": "TCS.NS",
            "INFOSYS": "INFY.NS",
            "RELIANCE": "RELIANCE.NS",
            "HDFC": "HDFCBANK.NS",
            "ICICI": "ICICIBANK.NS",
            "WIPRO": "WIPRO.NS",
            "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
            "TATA STEEL": "TATASTEEL.NS",
            "TESLA": "TSLA",
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT"
        }

        symbol = stock_map.get(company_name)
        if symbol:
            result = get_stock_price(symbol)
            if result:
                price, currency = result
                if currency == 'INR':
                    return f"The current price of {company_name} is ₹{price:.2f}."
                else:
                    # USD or other currencies
                    return f"The current price of {company_name} ({symbol}) is ${price:.2f} USD."
    return None
