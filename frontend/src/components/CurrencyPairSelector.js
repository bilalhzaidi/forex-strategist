import React, { useState, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';
import { forexAPI } from '../services/api';

const CurrencyPairSelector = ({ value, onChange, disabled = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [supportedPairs, setSupportedPairs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSupportedPairs();
  }, []);

  const loadSupportedPairs = async () => {
    try {
      setLoading(true);
      const data = await forexAPI.getSupportedPairs();
      setSupportedPairs(data.supported_pairs || []);
    } catch (error) {
      console.error('Error loading supported pairs:', error);
      // Fallback to common pairs
      setSupportedPairs([
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
        'AUD/USD', 'USD/CAD', 'NZD/USD', 'EUR/GBP',
        'EUR/JPY', 'GBP/JPY', 'CHF/JPY', 'EUR/CHF'
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredPairs = supportedPairs.filter(pair =>
    pair.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelect = (pair) => {
    onChange(pair);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full flex items-center justify-between px-4 py-3 text-left bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'
        }`}
      >
        <span className={value ? 'text-gray-900' : 'text-gray-500'}>
          {value || 'Select currency pair'}
        </span>
        <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search currency pairs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <div className="max-h-60 overflow-y-auto">
            {loading ? (
              <div className="p-3 text-center text-gray-500">
                Loading currency pairs...
              </div>
            ) : filteredPairs.length > 0 ? (
              filteredPairs.map((pair) => (
                <button
                  key={pair}
                  type="button"
                  onClick={() => handleSelect(pair)}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:bg-gray-50 ${
                    value === pair ? 'bg-primary-50 text-primary-700' : 'text-gray-900'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{pair}</span>
                    <span className="text-sm text-gray-500">
                      {pair.split('/').join(' to ')}
                    </span>
                  </div>
                </button>
              ))
            ) : (
              <div className="p-3 text-center text-gray-500">
                No currency pairs found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CurrencyPairSelector;