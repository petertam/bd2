#!/usr/bin/env python3
"""
Simple command-line test for Stock News Agent
Usage: python3 test_news_simple.py "news query"
Example: python3 test_news_simple.py "news for AAPL"
"""

import sys
import os
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.stock_news_agent import StockNewsAgent

# Load environment variables
load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_news_simple.py \"news query\"")
        print("Examples:")
        print("  python3 test_news_simple.py \"news for AAPL\"")
        print("  python3 test_news_simple.py \"Google news from 2025-01-01\"")
        print("  python3 test_news_simple.py \"Tesla news last 7 days\"")
        return
    
    query = " ".join(sys.argv[1:])
    
    print(f"🔍 Testing query: '{query}'")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        print("⚠️  No Alpha Vantage API key found in .env file")
        return
    
    # Create agent and process request
    agent = StockNewsAgent()
    
    try:
        response = agent.process_request(query)
        
        print(f"📝 Response Message:")
        print(response['message'])
        print()
        
        if response['data'] and response['data'].get('news_data'):
            print(f"📊 News Data:")
            print(response['data']['news_data'])
        else:
            print("📊 No news data returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 