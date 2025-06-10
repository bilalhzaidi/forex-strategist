import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..core.config import settings

class ForexAPIService:
    def __init__(self):
        self.base_url = settings.ALPHA_VANTAGE_BASE_URL
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Get real-time exchange rate from Alpha Vantage"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")
            
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'apikey': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'Realtime Currency Exchange Rate' in data:
                            rate_data = data['Realtime Currency Exchange Rate']
                            return {
                                'from_currency': rate_data['1. From_Currency Code'],
                                'to_currency': rate_data['3. To_Currency Code'],
                                'rate': float(rate_data['5. Exchange Rate']),
                                'last_refreshed': rate_data['6. Last Refreshed'],
                                'timezone': rate_data['7. Time Zone']
                            }
                        elif 'Error Message' in data:
                            raise ValueError(f"API Error: {data['Error Message']}")
                        elif 'Note' in data:
                            raise ValueError(f"API Rate Limit: {data['Note']}")
                    return None
            except Exception as e:
                print(f"Error fetching exchange rate: {str(e)}")
                return None
    
    async def get_daily_time_series(self, from_currency: str, to_currency: str, outputsize: str = "compact") -> Optional[Dict]:
        """Get daily time series data for technical analysis"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")
            
        params = {
            'function': 'FX_DAILY',
            'from_symbol': from_currency,
            'to_symbol': to_currency,
            'outputsize': outputsize,
            'apikey': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if f'Time Series FX (Daily)' in data:
                            return data['Time Series FX (Daily)']
                        elif 'Error Message' in data:
                            raise ValueError(f"API Error: {data['Error Message']}")
                        elif 'Note' in data:
                            raise ValueError(f"API Rate Limit: {data['Note']}")
                    return None
            except Exception as e:
                print(f"Error fetching time series data: {str(e)}")
                return None
    
    def calculate_moving_averages(self, time_series_data: Dict) -> Dict:
        """Calculate moving averages from time series data"""
        if not time_series_data:
            return {}
            
        # Convert to DataFrame for easier manipulation
        df_data = []
        for date, values in time_series_data.items():
            df_data.append({
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'close': float(values['4. close'])
            })
        
        df = pd.DataFrame(df_data)
        df = df.sort_values('date')
        
        # Calculate moving averages
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_50'] = df['close'].rolling(window=50).mean()
        
        # Get the latest values
        latest = df.iloc[-1]
        
        # Determine trend direction
        trend = "neutral"
        if len(df) >= 20:
            current_price = latest['close']
            ma_20 = latest['ma_20']
            
            if current_price > ma_20 and df.iloc[-2]['close'] > df.iloc[-3]['close']:
                trend = "upward"
            elif current_price < ma_20 and df.iloc[-2]['close'] < df.iloc[-3]['close']:
                trend = "downward"
        
        return {
            'moving_average_5': latest['ma_5'] if not pd.isna(latest['ma_5']) else None,
            'moving_average_20': latest['ma_20'] if not pd.isna(latest['ma_20']) else None,
            'moving_average_50': latest['ma_50'] if not pd.isna(latest['ma_50']) else None,
            'trend_direction': trend,
            'current_price': latest['close']
        }
    
    async def get_technical_analysis(self, currency_pair: str) -> Dict:
        """Get comprehensive technical analysis for a currency pair"""
        from_currency, to_currency = currency_pair.split('/')
        
        # Get current rate
        current_rate = await self.get_exchange_rate(from_currency, to_currency)
        
        # Get historical data for moving averages
        time_series = await self.get_daily_time_series(from_currency, to_currency)
        
        if not current_rate or not time_series:
            return {
                'current_rate': 0.0,
                'moving_average_5': None,
                'moving_average_20': None,
                'moving_average_50': None,
                'trend_direction': 'unknown',
                'summary': 'Unable to fetch technical data'
            }
        
        # Calculate technical indicators
        technical_data = self.calculate_moving_averages(time_series)
        
        # Generate summary
        summary = self._generate_technical_summary(technical_data, current_rate['rate'])
        
        return {
            'current_rate': current_rate['rate'],
            'moving_average_5': technical_data.get('moving_average_5'),
            'moving_average_20': technical_data.get('moving_average_20'),
            'moving_average_50': technical_data.get('moving_average_50'),
            'trend_direction': technical_data.get('trend_direction', 'unknown'),
            'summary': summary
        }
    
    def _generate_technical_summary(self, technical_data: Dict, current_rate: float) -> str:
        """Generate a summary of technical analysis"""
        trend = technical_data.get('trend_direction', 'unknown')
        ma_20 = technical_data.get('moving_average_20')
        
        ma_20_str = f"{ma_20:.4f}" if ma_20 else "N/A"
        
        if trend == 'upward':
            return f"Technical analysis shows an upward trend. Current rate ({current_rate:.4f}) is above the 20-day moving average ({ma_20_str}), indicating bullish momentum."
        elif trend == 'downward':
            return f"Technical analysis shows a downward trend. Current rate ({current_rate:.4f}) is below the 20-day moving average ({ma_20_str}), indicating bearish momentum."
        else:
            return f"Technical analysis shows a neutral trend. Current rate is {current_rate:.4f}. Market direction is unclear based on moving averages."