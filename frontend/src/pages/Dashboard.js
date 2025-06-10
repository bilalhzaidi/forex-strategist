import React, { useState } from 'react';
import { Play, RefreshCw, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import CurrencyPairSelector from '../components/CurrencyPairSelector';
import RecommendationCard from '../components/RecommendationCard';
import { forexAPI } from '../services/api';

const Dashboard = () => {
  const [selectedPair, setSelectedPair] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!selectedPair) {
      toast.error('Please select a currency pair');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await forexAPI.analyzeCurrencyPair(selectedPair);
      setRecommendation(result);
      toast.success('Analysis completed successfully!');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to analyze currency pair';
      setError(errorMessage);
      toast.error(errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (recommendation) {
      await handleAnalyze();
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Forex Trading Advisor
        </h1>
        <p className="text-lg text-gray-600">
          Get AI-powered buy/hold/sell recommendations based on technical analysis, 
          sentiment analysis, and market events
        </p>
      </div>

      {/* Analysis Controls */}
      <div className="card p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Currency Pair
            </label>
            <CurrencyPairSelector
              value={selectedPair}
              onChange={setSelectedPair}
              disabled={loading}
            />
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleAnalyze}
              disabled={loading || !selectedPair}
              className="btn btn-primary px-6 py-3 flex items-center space-x-2"
            >
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin" />
              ) : (
                <Play className="h-5 w-5" />
              )}
              <span>{loading ? 'Analyzing...' : 'Analyze'}</span>
            </button>

            {recommendation && (
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="btn btn-secondary px-4 py-3 flex items-center space-x-2"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            )}
          </div>

          {loading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />
                <div>
                  <p className="text-blue-800 font-medium">Analyzing {selectedPair}</p>
                  <p className="text-blue-600 text-sm">
                    Fetching forex data, analyzing market sentiment, and generating recommendations...
                  </p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <AlertCircle className="h-5 w-5 text-danger-600" />
                <div>
                  <p className="text-danger-800 font-medium">Analysis Failed</p>
                  <p className="text-danger-600 text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recommendation Display */}
      <RecommendationCard 
        recommendation={recommendation} 
        loading={loading}
      />

      {/* Quick Info */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card p-6 text-center">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Play className="h-6 w-6 text-primary-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Technical Analysis</h3>
          <p className="text-sm text-gray-600">
            Moving averages and trend analysis using live forex data from Alpha Vantage
          </p>
        </div>

        <div className="card p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Sentiment Analysis</h3>
          <p className="text-sm text-gray-600">
            Real-time news sentiment analysis from multiple financial news sources
          </p>
        </div>

        <div className="card p-6 text-center">
          <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <RefreshCw className="h-6 w-6 text-orange-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Event Detection</h3>
          <p className="text-sm text-gray-600">
            Macroeconomic and geopolitical event impact assessment
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;