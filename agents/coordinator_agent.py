import re
from typing import Optional
from .base_agent import BaseAgent
from .stock_quote_agent import StockQuoteAgent
from .stock_news_agent import StockNewsAgent
from .trading_advice_agent import TradingAdviceAgent

class CoordinatorAgent(BaseAgent):
    """Main coordinator agent that delegates requests to specialized agents"""
    
    def __init__(self):
        super().__init__("Coordinator Agent")
        
        # Initialize specialized agents
        self.stock_quote_agent = StockQuoteAgent()
        self.stock_news_agent = StockNewsAgent()
        self.trading_advice_agent = TradingAdviceAgent()
        
        # Current personality
        self.current_personality = "Warren Buffett"
    
    def process_request(self, message: str, context: Optional[dict] = None) -> dict:
        """Process user message and delegate to appropriate agent"""
        try:
            # Check if this is a personality change request
            if self.is_personality_change_request(message):
                return self.handle_personality_change(message)
            
            # Determine the intent of the message
            intent = self.classify_intent(message)
            
            # Route to appropriate agent based on intent
            if intent == "stock_quote":
                return self.handle_stock_quote_request(message)
            elif intent == "stock_news":
                return self.handle_stock_news_request(message)
            elif intent == "trading_advice":
                return self.handle_trading_advice_request(message)
            else:
                # Default to trading advice for general investment questions
                return self.handle_trading_advice_request(message)
                
        except Exception as e:
            print(f"Error in coordinator: {e}")
            return {
                'message': "I apologize, but I encountered an error processing your request. Please try again.",
                'personality': self.current_personality,
                'data': None
            }
    
    def process_message(self, message: str) -> dict:
        """Wrapper method for backward compatibility"""
        return self.process_request(message)
    
    def is_personality_change_request(self, message: str) -> bool:
        """Check if the message is requesting a personality change"""
        change_patterns = [
            r'change personality to (.+)',
            r'switch to (.+)',
            r'become (.+)',
            r'act like (.+)',
            r'be (.+)'
        ]
        
        for pattern in change_patterns:
            if re.search(pattern, message.lower()):
                return True
        return False
    
    def handle_personality_change(self, message: str) -> dict:
        """Handle personality change request"""
        # Extract personality name from message
        change_patterns = [
            r'change personality to (.+)',
            r'switch to (.+)',
            r'become (.+)',
            r'act like (.+)',
            r'be (.+)'
        ]
        
        for pattern in change_patterns:
            match = re.search(pattern, message.lower())
            if match:
                personality = match.group(1).strip()
                # Clean up the personality name
                personality = personality.replace('personality', '').strip()
                
                # Try to match with available personalities
                available_personalities = [
                    "Warren Buffett", "Peter Lynch", "Benjamin Graham", "George Soros",
                    "Cathie Wood", "Charlie Munger", "Michael Burry", "Phil Fisher",
                    "Rakesh Jhunjhunwala", "Stanley Druckenmiller", "Bill Ackman", "Aswath Damodaran"
                ]
                
                matched_personality = None
                for avail_personality in available_personalities:
                    if personality.lower() in avail_personality.lower():
                        matched_personality = avail_personality
                        break
                
                if matched_personality:
                    self.set_personality(matched_personality)
                    return {
                        'message': f"I've changed my personality to {matched_personality}. How can I help you with your investments?",
                        'personality': matched_personality,
                        'data': None
                    }
                else:
                    return {
                        'message': f"I'm sorry, I don't recognize the personality '{personality}'. Available personalities include Warren Buffett, Peter Lynch, Benjamin Graham, and others.",
                        'personality': self.current_personality,
                        'data': None
                    }
        
        return {
            'message': "I didn't understand the personality change request. Please try 'Change personality to [name]'.",
            'personality': self.current_personality,
            'data': None
        }
    
    def classify_intent(self, message: str) -> str:
        """Classify the intent of the user message"""
        message_lower = message.lower()
        
        # Stock quote keywords
        quote_keywords = [
            'price', 'quote', 'stock price', 'current price', 'trading at',
            'what is', 'how much', 'cost', 'value', 'worth', 'ohlc',
            'open', 'close', 'high', 'low', 'volume'
        ]
        
        # Stock news keywords
        news_keywords = [
            'news', 'headlines', 'articles', 'stories', 'reports',
            'latest', 'recent', 'updates', 'announcements', 'sentiment'
        ]
        
        # Trading advice keywords
        advice_keywords = [
            'should i buy', 'should i sell', 'invest', 'investment',
            'advice', 'recommend', 'opinion', 'analysis', 'outlook',
            'buy', 'sell', 'hold', 'portfolio', 'strategy'
        ]
        
        # Check for date patterns which might indicate historical data requests
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'on \w+',  # "on Monday", "on January"
            r'yesterday', r'last week', r'last month'
        ]
        
        has_date = any(re.search(pattern, message_lower) for pattern in date_patterns)
        
        # Score each intent
        quote_score = sum(1 for keyword in quote_keywords if keyword in message_lower)
        news_score = sum(1 for keyword in news_keywords if keyword in message_lower)
        advice_score = sum(1 for keyword in advice_keywords if keyword in message_lower)
        
        # If there's a date and quote keywords, it's likely a historical quote request
        if has_date and quote_score > 0:
            return "stock_quote"
        
        # Determine intent based on highest score
        if news_score > quote_score and news_score > advice_score:
            return "stock_news"
        elif quote_score > advice_score:
            return "stock_quote"
        else:
            return "trading_advice"
    
    def handle_stock_quote_request(self, message: str) -> dict:
        """Handle stock quote request"""
        response = self.stock_quote_agent.process_request(message)
        response['personality'] = self.current_personality
        return response
    
    def handle_stock_news_request(self, message: str) -> dict:
        """Handle stock news request"""
        response = self.stock_news_agent.process_request(message)
        response['personality'] = self.current_personality
        return response
    
    def handle_trading_advice_request(self, message: str) -> dict:
        """Handle trading advice request"""
        # Get additional context from other agents if ticker is mentioned
        context = {}
        
        # Check if there's a ticker in the message
        ticker = self.extract_ticker_from_text(message)
        if ticker:
            # Try to get recent stock data for context
            try:
                stock_response = self.stock_quote_agent.process_request(f"{ticker} current price")
                if stock_response.get('data') and stock_response['data'].get('stock_data'):
                    context['stock_data'] = stock_response['data']['stock_data']
            except:
                pass
            
            # Try to get recent news for context
            try:
                news_response = self.stock_news_agent.process_request(f"{ticker} news")
                if news_response.get('data') and news_response['data'].get('news_data'):
                    context['news_data'] = news_response['data']['news_data'][:500]  # Truncate for context
            except:
                pass
        
        # Get trading advice with context
        response = self.trading_advice_agent.process_request(message, context)
        return response
    
    def set_personality(self, personality: str):
        """Set the current personality for all agents"""
        self.current_personality = personality
        self.trading_advice_agent.set_personality(personality)
    
    def get_current_personality(self) -> str:
        """Get the current personality"""
        return self.current_personality 