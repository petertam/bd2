#!/usr/bin/env python3
"""
Test script for Trading Advice Agent
Tests the new format with buy/sell/hold recommendations and scores
"""

import sys
import os
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.trading_advice_agent import TradingAdviceAgent

# Load environment variables
load_dotenv()

def test_trading_advice_format():
    """Test the new trading advice format with recommendations and scores"""
    print("🚀 TESTING NEW TRADING ADVICE FORMAT")
    print("=" * 60)
    
    agent = TradingAdviceAgent()
    
    # Test different personalities and queries
    test_cases = [
        ("Warren Buffett", "Should I buy Apple stock?"),
        ("Peter Lynch", "What do you think about Tesla?"),
        ("Cathie Wood", "Is NVIDIA a good investment?"),
        ("Benjamin Graham", "Should I invest in Microsoft?"),
        ("George Soros", "What's your view on Amazon?"),
    ]
    
    for personality, query in test_cases:
        print(f"\n📊 Testing {personality}")
        print(f"Query: {query}")
        print("-" * 40)
        
        # Set personality
        agent.set_personality(personality)
        
        # Get advice
        response = agent.process_request(query)
        
        print(f"Response:")
        print(response['message'])
        print(f"Personality: {response['personality']}")
        print("=" * 60)

def main():
    """Run the test"""
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OpenAI API key found in .env file")
        return
    
    try:
        test_trading_advice_format()
        print("\n✅ TRADING ADVICE FORMAT TEST COMPLETED")
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 