import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from typing import Optional
from .base_agent import BaseAgent

class StockNewsAgent(BaseAgent):
    """Agent for fetching stock news and sentiment data"""
    
    def __init__(self):
        super().__init__("Stock News Agent")
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.data_folder = 'data'
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def process_request(self, message: str, context: Optional[dict] = None) -> dict:
        """Process stock news request"""
        ticker = self.extract_ticker_from_text(message)
        
        if not ticker:
            return {
                'message': "I couldn't identify a stock ticker in your message. Please specify a stock symbol (e.g., AAPL, MSFT, TSLA).",
                'data': None
            }
        
        # Extract date range from message
        date_range = self.extract_date_range_from_text(message)
        
        try:
            print(f"DEBUG: Processing news request for {ticker} with date range: {date_range}")
            news_data = self.get_news_data(ticker, date_range)
            if news_data:
                return {
                    'message': f"Here's the latest news for {ticker}:",
                    'data': {'news_data': news_data}
                }
            else:
                return {
                    'message': f"Sorry, I couldn't find recent news for {ticker}. Date range: {date_range['start_date']} to {date_range['end_date']}",
                    'data': None
                }
                
        except Exception as e:
            print(f"Error processing stock news request: {e}")
            return {
                'message': "I encountered an error while fetching news data. Please try again.",
                'data': None
            }
    
    def extract_date_range_from_text(self, text: str) -> dict:
        """Extract date range from text message"""
        # Default to last 30 days (from 30 days ago to today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Look for date patterns in text
        import re
        
        # Flag to track if we found any date pattern
        found_date_pattern = False
        
        # Look for "from X to Y" patterns
        from_to_pattern = r'from\s+([^to]+)\s+to\s+([^\s]+)'
        match = re.search(from_to_pattern, text.lower())
        
        if match:
            found_date_pattern = True
            try:
                start_str = match.group(1).strip()
                end_str = match.group(2).strip()
                
                # Parse dates - don't assume current year, let dateutil handle it
                start_date = parse(start_str, fuzzy=True)
                end_date = parse(end_str, fuzzy=True)
                
                print(f"DEBUG: Parsed date range: {start_date} to {end_date}")
                    
            except Exception as e:
                print(f"DEBUG: Error parsing date range: {e}")
                found_date_pattern = False
        else:
            # Look for "from X" pattern (without "to")
            from_only_pattern = r'from\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s|$)'
            match = re.search(from_only_pattern, text.lower())
            
            if match:
                found_date_pattern = True
                try:
                    start_str = match.group(1).strip()
                    
                    # Parse the start date
                    start_date = parse(start_str, fuzzy=True)
                    
                    # Calculate end date: 30 days after start date, but not more than today
                    potential_end_date = start_date + timedelta(days=30)
                    today = datetime.now()
                    
                    # Use the earlier of: (start_date + 30 days) or today
                    end_date = min(potential_end_date, today)
                    
                    print(f"DEBUG: Parsed 'from' only date: {start_date} to {end_date}")
                        
                except Exception as e:
                    print(f"DEBUG: Error parsing 'from' date: {e}")
                    found_date_pattern = False
        
        # Look for "last X days/weeks" patterns
        last_pattern = r'last\s+(\d+)\s+(day|week|month)s?'
        match = re.search(last_pattern, text.lower())
        
        if match:
            found_date_pattern = True
            try:
                number = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'day':
                    start_date = end_date - timedelta(days=number)
                elif unit == 'week':
                    start_date = end_date - timedelta(weeks=number)
                elif unit == 'month':
                    start_date = end_date - timedelta(days=number * 30)
                    
                print(f"DEBUG: Parsed 'last' pattern: {start_date} to {end_date}")
            except Exception as e:
                print(f"DEBUG: Error parsing 'last' pattern: {e}")
                found_date_pattern = False
        
        # If no date pattern was found, use default (last 30 days)
        if not found_date_pattern:
            print(f"DEBUG: No date pattern found, using default last 30 days: {start_date} to {end_date}")
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    
    def get_news_data(self, ticker: str, date_range: dict) -> str:
        """Get news data for ticker within date range"""
        try:
            # Check cache first
            cache_file = os.path.join(self.data_folder, f"{ticker}_news.csv")
            cached_data = None
            
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file)
                df['Date'] = pd.to_datetime(df['Date'])
                
                start_date = pd.to_datetime(date_range['start_date'])
                end_date = pd.to_datetime(date_range['end_date'])
                
                # Filter by date range
                filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
                
                if not filtered_df.empty:
                    cached_data = self.format_news_data(filtered_df, ticker)
                    print(f"DEBUG: Found {len(filtered_df)} cached news items for {ticker}")
                    print(f"DEBUG: Returning cached data for {ticker}")
                    return cached_data
                else:
                    print(f"DEBUG: No cached data found for {ticker} in date range {date_range['start_date']} to {date_range['end_date']}")
            else:
                print(f"DEBUG: No cache file found for {ticker}")
            
            # Fetch from API only if no cached data was found
            print(f"DEBUG: Fetching from Alpha Vantage API for {ticker}")
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': self.api_key,
                'limit': 50
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            print(f"DEBUG: Alpha Vantage API response keys: {list(data.keys())}")
            
            if 'feed' in data:
                news_items = data['feed']
                print(f"DEBUG: Found {len(news_items)} news items from API")
                
                # Save to cache
                self.save_news_to_cache(ticker, news_items)
                
                # Filter by date range
                filtered_news = self.filter_news_by_date(news_items, date_range)
                print(f"DEBUG: After date filtering: {len(filtered_news)} news items")
                
                if filtered_news:
                    return self.format_api_news_data(filtered_news, ticker)
                else:
                    return f"No news found for {ticker} in the date range {date_range['start_date']} to {date_range['end_date']}. Try a different date range or check if the dates are in the future."
            else:
                print(f"DEBUG: API response error: {data}")
                return f"Error retrieving news from Alpha Vantage API. Response: {data}"
                
        except Exception as e:
            print(f"Error fetching news data: {e}")
            return "Unable to retrieve news data due to an error."
    
    def save_news_to_cache(self, ticker: str, news_items: list):
        """Save news data to CSV cache"""
        try:
            # Skip if no news items to save
            if not news_items:
                print(f"DEBUG: No news items to save for {ticker}")
                return
                
            cache_file = os.path.join(self.data_folder, f"{ticker}_news.csv")
            
            # Convert to DataFrame
            rows = []
            for item in news_items:
                # Extract relevant ticker sentiment
                ticker_sentiment = None
                relevance = 0
                
                if 'ticker_sentiment' in item:
                    for ts in item['ticker_sentiment']:
                        if ts['ticker'] == ticker:
                            ticker_sentiment = ts['ticker_sentiment_label']
                            relevance = float(ts['relevance_score'])
                            break
                
                rows.append({
                    'Date': item['time_published'][:8],  # YYYYMMDD format
                    'title': item['title'],
                    'description': item['summary'][:500],  # Truncate long descriptions
                    'url': item['url'],
                    'source': item['source'],
                    'sentiment': ticker_sentiment or 'Neutral',
                    'relevance': relevance
                })
            
            # Skip if no rows were created
            if not rows:
                print(f"DEBUG: No valid rows created for {ticker}")
                return
            
            new_df = pd.DataFrame(rows)
            new_df['Date'] = pd.to_datetime(new_df['Date'], format='%Y%m%d')
            
            # If cache exists, merge with existing data
            if os.path.exists(cache_file):
                existing_df = pd.read_csv(cache_file)
                existing_df['Date'] = pd.to_datetime(existing_df['Date'])
                
                # Combine and remove duplicates
                combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['title', 'Date'])
                combined_df = combined_df.sort_values('Date', ascending=False)
            else:
                combined_df = new_df.sort_values('Date', ascending=False)
            
            # Save to cache
            combined_df.to_csv(cache_file, index=False)
            print(f"DEBUG: Saved {len(rows)} news items to cache for {ticker}")
            
        except Exception as e:
            print(f"Error saving news to cache: {e}")
    
    def filter_news_by_date(self, news_items: list, date_range: dict) -> list:
        """Filter news items by date range"""
        try:
            start_date = datetime.strptime(date_range['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(date_range['end_date'], '%Y-%m-%d')
            
            filtered_items = []
            for item in news_items:
                item_date = datetime.strptime(item['time_published'][:8], '%Y%m%d')
                if start_date <= item_date <= end_date:
                    filtered_items.append(item)
            
            return filtered_items
        except Exception as e:
            print(f"Error filtering news by date: {e}")
            return news_items  # Return all if filtering fails
    
    def format_news_data(self, df: pd.DataFrame, ticker: str) -> str:
        """Format news data from DataFrame"""
        result = f"Recent news for {ticker}:\n\n"
        
        # Sort by date and take top 5
        df_sorted = df.sort_values('Date', ascending=False).head(5)
        
        for idx, row in df_sorted.iterrows():
            result += f"📰 {row['title']}\n"
            result += f"📅 {row['Date'].strftime('%Y-%m-%d')}\n"
            result += f"📊 Sentiment: {row['sentiment']}\n"
            result += f"📈 Relevance: {row['relevance']:.2f}\n"
            result += f"🔗 Source: {row['source']}\n"
            result += f"📝 {row['description'][:200]}...\n"
            result += f"🌐 {row['url']}\n\n"
        
        return result
    
    def format_api_news_data(self, news_items: list, ticker: str) -> str:
        """Format news data from API response"""
        result = f"Recent news for {ticker}:\n\n"
        
        for item in news_items[:5]:  # Show top 5 items
            # Extract ticker sentiment
            sentiment = 'Neutral'
            relevance = 0
            
            if 'ticker_sentiment' in item:
                for ts in item['ticker_sentiment']:
                    if ts['ticker'] == ticker:
                        sentiment = ts['ticker_sentiment_label']
                        relevance = float(ts['relevance_score'])
                        break
            
            # Format date
            date_str = item['time_published'][:8]
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            result += f"📰 {item['title']}\n"
            result += f"📅 {formatted_date}\n"
            result += f"📊 Sentiment: {sentiment}\n"
            result += f"📈 Relevance: {relevance:.2f}\n"
            result += f"🔗 Source: {item['source']}\n"
            result += f"📝 {item['summary'][:200]}...\n"
            result += f"🌐 {item['url']}\n\n"
        
        return result 