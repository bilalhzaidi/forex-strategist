import re
from typing import List, Optional

def validate_currency_pair(currency_pair: str) -> bool:
    """Validate currency pair format (e.g., EUR/USD)"""
    if not currency_pair:
        return False
    
    pattern = r'^[A-Z]{3}/[A-Z]{3}$'
    return bool(re.match(pattern, currency_pair))

def validate_currency_code(currency: str) -> bool:
    """Validate individual currency code"""
    if not currency:
        return False
    
    return len(currency) == 3 and currency.isalpha() and currency.isupper()

def get_major_currency_pairs() -> List[str]:
    """Get list of major currency pairs"""
    return [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
        "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
        "EUR/JPY", "GBP/JPY", "CHF/JPY", "EUR/CHF",
        "AUD/JPY", "GBP/CHF", "AUD/NZD", "EUR/AUD",
        "EUR/CAD", "GBP/AUD", "GBP/CAD", "USD/ZAR"
    ]

def is_supported_currency_pair(currency_pair: str) -> bool:
    """Check if currency pair is supported"""
    return currency_pair in get_major_currency_pairs()

def normalize_currency_pair(currency_pair: str) -> Optional[str]:
    """Normalize currency pair format"""
    if not currency_pair:
        return None
    
    # Remove spaces and convert to uppercase
    normalized = currency_pair.replace(' ', '').upper()
    
    # Handle different separators
    for sep in ['-', '_', ':', ' ']:
        if sep in normalized:
            normalized = normalized.replace(sep, '/')
    
    # Validate format
    if validate_currency_pair(normalized):
        return normalized
    
    return None