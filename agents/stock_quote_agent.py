import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from .base_agent import BaseAgent

class StockQuoteAgent(BaseAgent):
    """Agent for fetching stock quotes and price data"""
    
    def __init__(self):
        super().__init__("Stock Quote Agent")
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.data_folder = 'data'
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def process_request(self, message: str, context: dict = None) -> dict:
        """Process stock quote request"""
        ticker = self.extract_ticker_from_text(message)
        
        if not ticker:
            return {
                'message': "I couldn't identify a stock ticker in your message. Please specify a stock symbol (e.g., AAPL, MSFT, TSLA).",
                'data': None
            }
        
        # Extract date from message if present
        date_str = self.extract_date_from_text(message)
        
        try:
            if date_str:
                # Get historical data for specific date
                stock_data = self.get_historical_data(ticker, date_str)
                if stock_data:
                    # Check if it's a holiday/weekend message (starts with ticker name)
                    if stock_data.strip().startswith(f"{ticker} stock data is not available"):
                        return {
                            'message': stock_data,
                            'data': None
                        }
                    else:
                        return {
                            'message': f"Here's the stock data for {ticker} on {date_str}:",
                            'data': {'stock_data': stock_data}
                        }
                else:
                    return {
                        'message': f"Sorry, I couldn't find stock data for {ticker} on {date_str}.",
                        'data': None
                    }
            else:
                # Get current/latest data
                stock_data = self.get_current_data(ticker)
                if stock_data:
                    return {
                        'message': f"Here's the current stock data for {ticker}:",
                        'data': {'stock_data': stock_data}
                    }
                else:
                    return {
                        'message': f"Sorry, I couldn't fetch current data for {ticker}.",
                        'data': None
                    }
                    
        except Exception as e:
            print(f"Error processing stock quote request: {e}")
            return {
                'message': "I encountered an error while fetching stock data. Please try again.",
                'data': None
            }
    
    def extract_date_from_text(self, text: str) -> str:
        """Extract date from text message"""
        # Simple date extraction - can be enhanced
        date_keywords = ['on', 'for', 'at', 'during']
        words = text.lower().split()
        
        for i, word in enumerate(words):
            if word in date_keywords and i + 1 < len(words):
                try:
                    # Try to parse the next few words as a date
                    date_part = ' '.join(words[i+1:i+4])
                    parsed_date = parse(date_part, fuzzy=True)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        # Look for common date patterns
        import re
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    parsed_date = parse(match.group(), fuzzy=True)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        return None
    
    def get_current_data(self, ticker: str) -> str:
        """Get current stock data"""
        try:
            # First try to get from cache (today's data)
            cache_file = os.path.join(self.data_folder, f"{ticker}_data.csv")
            
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file)
                df['Date'] = pd.to_datetime(df['Date'])
                latest_date = df['Date'].max()
                
                # If we have today's data, return it
                if latest_date.date() == datetime.now().date():
                    latest_row = df[df['Date'] == latest_date].iloc[0]
                    return self.format_stock_data(latest_row, ticker)
            
            # Fetch from API
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'apikey': self.api_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                latest_date = max(time_series.keys())
                latest_data = time_series[latest_date]
                
                # Save to cache
                self.save_to_cache(ticker, {latest_date: latest_data})
                
                return self.format_current_data(latest_data, ticker, latest_date)
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching current data: {e}")
            return None
    
    def get_historical_data(self, ticker: str, date_str: str) -> str:
        """Get historical stock data for specific date"""
        try:
            # Check cache first
            cache_file = os.path.join(self.data_folder, f"{ticker}_data.csv")
            
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file)
                df['Date'] = pd.to_datetime(df['Date'])
                
                target_date = pd.to_datetime(date_str)
                matching_rows = df[df['Date'].dt.date == target_date.date()]
                
                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    return self.format_stock_data(row, ticker)
            
            # Fetch from API if not in cache
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'apikey': self.api_key,
                'outputsize': 'full'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                
                # Save all data to cache
                self.save_to_cache(ticker, time_series)
                
                # Find the specific date
                if date_str in time_series:
                    stock_data = time_series[date_str]
                    return self.format_historical_data(stock_data, ticker, date_str)
                else:
                    # Check if it's a weekend or potential holiday
                    return self.get_holiday_message(ticker, date_str, time_series)
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
    
    def save_to_cache(self, ticker: str, time_series_data: dict):
        """Save stock data to CSV cache"""
        try:
            cache_file = os.path.join(self.data_folder, f"{ticker}_data.csv")
            
            # Convert to DataFrame
            rows = []
            for date, data in time_series_data.items():
                rows.append({
                    'Date': date,
                    'Open': data['1. open'],
                    'High': data['2. high'],
                    'Low': data['3. low'],
                    'Close': data['4. close'],
                    'Volume': data['5. volume']
                })
            
            new_df = pd.DataFrame(rows)
            new_df['Date'] = pd.to_datetime(new_df['Date'])
            
            # If cache exists, merge with existing data
            if os.path.exists(cache_file):
                existing_df = pd.read_csv(cache_file)
                existing_df['Date'] = pd.to_datetime(existing_df['Date'])
                
                # Combine and remove duplicates
                combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['Date'])
                combined_df = combined_df.sort_values('Date', ascending=False)
            else:
                combined_df = new_df.sort_values('Date', ascending=False)
            
            # Save to cache
            combined_df.to_csv(cache_file, index=False)
            
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def format_current_data(self, data: dict, ticker: str, date: str) -> str:
        """Format current stock data for display"""
        return f"""
{ticker} Stock Price - {date}
Current Price: ${float(data['4. close']):.2f}
Open: ${float(data['1. open']):.2f}
High: ${float(data['2. high']):.2f}
Low: ${float(data['3. low']):.2f}
Volume: {int(data['5. volume']):,}
"""
    
    def format_historical_data(self, data: dict, ticker: str, date: str) -> str:
        """Format historical stock data for display"""
        return f"""
{ticker} Stock Price - {date}
Open: ${float(data['1. open']):.2f}
High: ${float(data['2. high']):.2f}
Low: ${float(data['3. low']):.2f}
Close: ${float(data['4. close']):.2f}
Volume: {int(data['5. volume']):,}
"""
    
    def format_stock_data(self, row, ticker: str) -> str:
        """Format stock data from DataFrame row"""
        return f"""
{ticker} Stock Price - {row['Date']}
Open: ${float(row['Open']):.2f}
High: ${float(row['High']):.2f}
Low: ${float(row['Low']):.2f}
Close: ${float(row['Close']):.2f}
Volume: {int(row['Volume']):,}
"""
    
    def get_holiday_message(self, ticker: str, date_str: str, time_series: dict) -> str:
        """Generate a meaningful message when stock data is not available for a specific date"""
        from datetime import datetime
        
        try:
            # Parse the requested date
            requested_date = datetime.strptime(date_str, '%Y-%m-%d')
            day_of_week = requested_date.strftime('%A')
            
            # Check if it's a weekend
            if requested_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return f"""
{ticker} stock data is not available for {date_str} ({day_of_week}).

The stock market is closed on weekends. Please try a weekday date instead.

💡 Tip: Stock markets typically operate Monday through Friday, excluding holidays.
"""
            
            # Find the closest trading day with data
            closest_date = None
            closest_data = None
            min_diff = float('inf')
            
            for available_date, data in time_series.items():
                try:
                    avail_date = datetime.strptime(available_date, '%Y-%m-%d')
                    diff = abs((avail_date - requested_date).days)
                    if diff < min_diff:
                        min_diff = diff
                        closest_date = available_date
                        closest_data = data
                except:
                    continue
            
            if closest_date and closest_data:
                return f"""
{ticker} stock data is not available for {date_str} ({day_of_week}).

This date may be a market holiday or the market may have been closed.

Here's the closest available trading data from {closest_date}:
{self.format_historical_data(closest_data, ticker, closest_date)}

💡 Tip: Stock markets are closed on federal holidays like New Year's Day, Independence Day, Thanksgiving, Christmas, etc.
"""
            else:
                return f"""
{ticker} stock data is not available for {date_str} ({day_of_week}).

This date may be a market holiday, weekend, or the market may have been closed.

💡 Tip: Stock markets are typically closed on weekends and federal holidays.
"""
                
        except Exception as e:
            return f"""
{ticker} stock data is not available for {date_str}.

This date may be a market holiday, weekend, or the market may have been closed.

💡 Tip: Stock markets are typically closed on weekends and federal holidays.
""" 