import os
import openai
from dotenv import load_dotenv
from abc import ABC, abstractmethod

load_dotenv()

class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, name: str):
        self.name = name
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    @abstractmethod
    def process_request(self, message: str, context: dict = None) -> dict:
        """Process a request and return a response"""
        pass
    
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """Generate a response using OpenAI"""
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    def extract_ticker_from_text(self, text: str) -> str:
        """Extract stock ticker from text"""
        # Enhanced implementation with comprehensive company name mapping
        text_upper = text.upper()
        
        # Comprehensive stock tickers mapping
        ticker_map = {
            # Technology Companies
            'APPLE': 'AAPL',
            'APPLE INC': 'AAPL',
            'MICROSOFT': 'MSFT',
            'MICROSOFT CORP': 'MSFT',
            'MICROSOFT CORPORATION': 'MSFT',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'ALPHABET INC': 'GOOGL',
            'AMAZON': 'AMZN',
            'AMAZON.COM': 'AMZN',
            'AMAZON COM': 'AMZN',
            'TESLA': 'TSLA',
            'TESLA INC': 'TSLA',
            'TESLA MOTORS': 'TSLA',
            'META': 'META',
            'META PLATFORMS': 'META',
            'FACEBOOK': 'META',
            'NETFLIX': 'NFLX',
            'NETFLIX INC': 'NFLX',
            'PAYPAL': 'PYPL',
            'PAYPAL HOLDINGS': 'PYPL',
            'NVIDIA': 'NVDA',
            'NVIDIA CORP': 'NVDA',
            'NVIDIA CORPORATION': 'NVDA',
            'INTEL': 'INTC',
            'INTEL CORP': 'INTC',
            'INTEL CORPORATION': 'INTC',
            'ADOBE': 'ADBE',
            'ADOBE INC': 'ADBE',
            'SALESFORCE': 'CRM',
            'SALESFORCE.COM': 'CRM',
            'ORACLE': 'ORCL',
            'ORACLE CORP': 'ORCL',
            'ORACLE CORPORATION': 'ORCL',
            'IBM': 'IBM',
            'INTERNATIONAL BUSINESS MACHINES': 'IBM',
            'CISCO': 'CSCO',
            'CISCO SYSTEMS': 'CSCO',
            'QUALCOMM': 'QCOM',
            'QUALCOMM INC': 'QCOM',
            'BROADCOM': 'AVGO',
            'BROADCOM INC': 'AVGO',
            'ADVANCED MICRO DEVICES': 'AMD',
            'AMD': 'AMD',
            
            # Financial Services
            'BERKSHIRE HATHAWAY': 'BRK.A',
            'BERKSHIRE': 'BRK.A',
            'JPMORGAN': 'JPM',
            'JP MORGAN': 'JPM',
            'JPMORGAN CHASE': 'JPM',
            'BANK OF AMERICA': 'BAC',
            'WELLS FARGO': 'WFC',
            'GOLDMAN SACHS': 'GS',
            'MORGAN STANLEY': 'MS',
            'AMERICAN EXPRESS': 'AXP',
            'VISA': 'V',
            'VISA INC': 'V',
            'MASTERCARD': 'MA',
            'MASTERCARD INC': 'MA',
            
            # Healthcare & Pharmaceuticals
            'JOHNSON & JOHNSON': 'JNJ',
            'JOHNSON AND JOHNSON': 'JNJ',
            'PFIZER': 'PFE',
            'PFIZER INC': 'PFE',
            'MODERNA': 'MRNA',
            'MODERNA INC': 'MRNA',
            'ABBVIE': 'ABBV',
            'ABBVIE INC': 'ABBV',
            'MERCK': 'MRK',
            'MERCK & CO': 'MRK',
            'BRISTOL MYERS SQUIBB': 'BMY',
            'BRISTOL-MYERS SQUIBB': 'BMY',
            'ELI LILLY': 'LLY',
            'LILLY': 'LLY',
            'UNITEDHEALTH': 'UNH',
            'UNITED HEALTH': 'UNH',
            'UNITEDHEALTH GROUP': 'UNH',
            
            # Consumer & Retail
            'WALMART': 'WMT',
            'WALMART INC': 'WMT',
            'PROCTER & GAMBLE': 'PG',
            'PROCTER AND GAMBLE': 'PG',
            'COCA COLA': 'KO',
            'COCA-COLA': 'KO',
            'PEPSI': 'PEP',
            'PEPSICO': 'PEP',
            'NIKE': 'NKE',
            'NIKE INC': 'NKE',
            'MCDONALD\'S': 'MCD',
            'MCDONALDS': 'MCD',
            'STARBUCKS': 'SBUX',
            'STARBUCKS CORP': 'SBUX',
            'HOME DEPOT': 'HD',
            'THE HOME DEPOT': 'HD',
            'DISNEY': 'DIS',
            'WALT DISNEY': 'DIS',
            'THE WALT DISNEY COMPANY': 'DIS',
            
            # Industrial & Energy
            'EXXON MOBIL': 'XOM',
            'EXXON': 'XOM',
            'CHEVRON': 'CVX',
            'CHEVRON CORP': 'CVX',
            'GENERAL ELECTRIC': 'GE',
            'GE': 'GE',
            'BOEING': 'BA',
            'BOEING CO': 'BA',
            'CATERPILLAR': 'CAT',
            'CATERPILLAR INC': 'CAT',
            '3M': 'MMM',
            '3M COMPANY': 'MMM',
            
            # Communication Services
            'VERIZON': 'VZ',
            'VERIZON COMMUNICATIONS': 'VZ',
            'AT&T': 'T',
            'ATT': 'T',
            'COMCAST': 'CMCSA',
            'COMCAST CORP': 'CMCSA',
            'TWITTER': 'TWTR',
            'TWITTER INC': 'TWTR',
            
            # Electric Vehicles & Clean Energy
            'RIVIAN': 'RIVN',
            'RIVIAN AUTOMOTIVE': 'RIVN',
            'LUCID': 'LCID',
            'LUCID MOTORS': 'LCID',
            'LUCID GROUP': 'LCID',
            'NIO': 'NIO',
            'NIO INC': 'NIO',
            'FORD': 'F',
            'FORD MOTOR': 'F',
            'FORD MOTOR COMPANY': 'F',
            'GENERAL MOTORS': 'GM',
            'GM': 'GM',
            
            # Cryptocurrency Related
            'COINBASE': 'COIN',
            'COINBASE GLOBAL': 'COIN',
            'MICROSTRATEGY': 'MSTR',
            'MICROSTRATEGY INC': 'MSTR',
            
            # Emerging Tech
            'PALANTIR': 'PLTR',
            'PALANTIR TECHNOLOGIES': 'PLTR',
            'SNOWFLAKE': 'SNOW',
            'SNOWFLAKE INC': 'SNOW',
            'ZOOM': 'ZM',
            'ZOOM VIDEO': 'ZM',
            'ZOOM VIDEO COMMUNICATIONS': 'ZM',
            'SLACK': 'WORK',
            'SLACK TECHNOLOGIES': 'WORK',
            'SHOPIFY': 'SHOP',
            'SHOPIFY INC': 'SHOP',
            'SQUARE': 'SQ',
            'BLOCK': 'SQ',
            'BLOCK INC': 'SQ',
            'UBER': 'UBER',
            'UBER TECHNOLOGIES': 'UBER',
            'LYFT': 'LYFT',
            'LYFT INC': 'LYFT',
            'AIRBNB': 'ABNB',
            'AIRBNB INC': 'ABNB',
            'DOORDASH': 'DASH',
            'DOORDASH INC': 'DASH',
            'SPOTIFY': 'SPOT',
            'SPOTIFY TECHNOLOGY': 'SPOT',
            'ROBLOX': 'RBLX',
            'ROBLOX CORP': 'RBLX',
            'PELOTON': 'PTON',
            'PELOTON INTERACTIVE': 'PTON'
        }
        
        # First, check for direct ticker mentions (highest priority)
        words = text_upper.split()
        for word in words:
            word = word.strip('.,!?()[]{}')
            if len(word) >= 2 and len(word) <= 5 and word.isalpha():
                if word in ticker_map.values():
                    return word
        
        # Then try to find exact company name matches
        for company_name, ticker in ticker_map.items():
            if company_name in text_upper:
                return ticker
        
        # Finally, check for partial matches (fuzzy matching) - more restrictive
        for word in words:
            word = word.strip('.,!?()[]{}')
            if len(word) >= 4:  # Require at least 4 characters to avoid false matches
                for company_name, ticker in ticker_map.items():
                    # Only match if word is a significant part of the company name
                    if (len(word) >= len(company_name) * 0.4 and 
                        (word in company_name or company_name.startswith(word))):
                        return ticker
        
        return "" 