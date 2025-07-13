# Multi-Agent System for Investment Advice
# This package contains various agents for stock analysis and investment advice

from .coordinator_agent import CoordinatorAgent
from .stock_quote_agent import StockQuoteAgent
from .stock_news_agent import StockNewsAgent
from .trading_advice_agent import TradingAdviceAgent

__all__ = ['CoordinatorAgent', 'StockQuoteAgent', 'StockNewsAgent', 'TradingAdviceAgent'] 