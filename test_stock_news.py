#!/usr/bin/env python3
"""
Test script for Stock News Agent
Tests various date range scenarios and API functionality
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.stock_news_agent import StockNewsAgent

# Load environment variables
load_dotenv()

def test_date_range_extraction():
    """Test date range extraction from various text patterns"""
    print("=" * 60)
    print("TESTING DATE RANGE EXTRACTION")
    print("=" * 60)
    
    agent = StockNewsAgent()
    
    test_cases = [
        # No date specified - should default to last 30 days
        ("news for GOOGLE", "Default last 30 days"),
        ("Get me Apple news", "Default last 30 days"),
        
        # From date only
        ("news of PAYPAL from 2025-01-01", "From date only"),
        ("TSLA news from yesterday", "From date with relative term"),
        
        # Date range
        ("news of AAPL from 2025-01-01 to 2025-01-15", "Full date range"),
        ("Microsoft news from 2024-12-01 to 2024-12-31", "Full date range"),
        
        # Last X days/weeks/months
        ("news for NVDA last 7 days", "Last X days"),
        ("Amazon news last 2 weeks", "Last X weeks"),
        ("META news last 1 month", "Last X months"),
    ]
    
    for text, description in test_cases:
        print(f"\nTesting: {text}")
        print(f"Description: {description}")
        date_range = agent.extract_date_range_from_text(text)
        print(f"Result: {date_range['start_date']} to {date_range['end_date']}")
        print("-" * 40)

def test_ticker_extraction():
    """Test ticker extraction from various text patterns"""
    print("\n" + "=" * 60)
    print("TESTING TICKER EXTRACTION")
    print("=" * 60)
    
    agent = StockNewsAgent()
    
    test_cases = [
        "news for GOOGLE",
        "Apple news",
        "Get me TSLA updates",
        "Microsoft stock news",
        "PayPal news from yesterday",
        "Amazon latest news",
        "META news last week",
        "NVDA stock updates",
        "news for XYZ123",  # Invalid ticker
    ]
    
    for text in test_cases:
        ticker = agent.extract_ticker_from_text(text)
        print(f"Text: '{text}' -> Ticker: {ticker}")

def test_live_news_api():
    """Test live news API calls"""
    print("\n" + "=" * 60)
    print("TESTING LIVE NEWS API")
    print("=" * 60)
    
    agent = StockNewsAgent()
    
    if not agent.api_key:
        print("⚠️  No Alpha Vantage API key found. Skipping live API tests.")
        return
    
    # Test cases with different companies and date ranges
    test_cases = [
        ("AAPL", "Apple - No date (default last 30 days)"),
        ("GOOGL", "Google - No date (default last 30 days)"),
        ("TSLA", "Tesla - No date (default last 30 days)"),
    ]
    
    for ticker, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"Ticker: {ticker}")
        
        # Create a default date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_range = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            result = agent.get_news_data(ticker, date_range)
            if result:
                print(f"✅ Success: Found news data")
                print(f"Preview: {result[:200]}...")
            else:
                print(f"❌ No news data returned")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

def test_process_request():
    """Test the full process_request method"""
    print("\n" + "=" * 60)
    print("TESTING FULL PROCESS REQUEST")
    print("=" * 60)
    
    agent = StockNewsAgent()
    
    test_messages = [
        "news for GOOGLE",
        "Apple news from last week",
        "TSLA news from 2025-01-01",
        "Microsoft news from 2024-12-01 to 2024-12-31",
        "Get me some news",  # No ticker
        "INVALID_TICKER news",  # Invalid ticker
    ]
    
    for message in test_messages:
        print(f"\nTesting message: '{message}'")
        try:
            response = agent.process_request(message)
            print(f"Response message: {response['message']}")
            if response['data']:
                print(f"Data available: Yes")
            else:
                print(f"Data available: No")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 40)

def test_cache_functionality():
    """Test CSV cache functionality"""
    print("\n" + "=" * 60)
    print("TESTING CACHE FUNCTIONALITY")
    print("=" * 60)
    
    agent = StockNewsAgent()
    
    # Check if cache files exist
    cache_dir = agent.data_folder
    print(f"Cache directory: {cache_dir}")
    
    if os.path.exists(cache_dir):
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('_news.csv')]
        print(f"Found {len(cache_files)} cache files:")
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            file_size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  - {file} ({file_size} bytes, modified: {mod_time})")
    else:
        print("Cache directory does not exist")

def main():
    """Run all tests"""
    print("🚀 STOCK NEWS AGENT TEST SUITE")
    print("Testing various functionality of the Stock News Agent")
    print()
    
    # Check if API key is available
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if api_key:
        print(f"✅ Alpha Vantage API key found: {api_key[:10]}...")
    else:
        print("⚠️  No Alpha Vantage API key found. Some tests will be skipped.")
    
    try:
        # Run all tests
        test_date_range_extraction()
        test_ticker_extraction()
        test_cache_functionality()
        test_process_request()
        
        # Only run live API tests if API key is available
        if api_key:
            test_live_news_api()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 