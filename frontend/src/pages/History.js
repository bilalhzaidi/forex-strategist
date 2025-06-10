import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, TrendingDown, Minus, RefreshCw, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';
import CurrencyPairSelector from '../components/CurrencyPairSelector';
import { forexAPI } from '../services/api';

const History = () => {
  const [selectedPair, setSelectedPair] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedPair) {
      loadHistory();
    }
  }, [selectedPair]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadHistory = async () => {
    if (!selectedPair) return;

    setLoading(true);
    setError(null);

    try {
      const data = await forexAPI.getRecommendationHistory(selectedPair, 50);
      setRecommendations(Array.isArray(data) ? data : []);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to load recommendation history';
      setError(errorMessage);
      toast.error(errorMessage);
      console.error('History error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'buy':
        return <TrendingUp className="h-4 w-4" />;
      case 'sell':
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  const getRecommendationColor = (type) => {
    switch (type) {
      case 'buy':
        return 'text-success-600 bg-success-100';
      case 'sell':
        return 'text-danger-600 bg-danger-100';
      default:
        return 'text-warning-600 bg-warning-100';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };


  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Recommendation History
        </h1>
        <p className="text-lg text-gray-600">
          View historical trading recommendations and their performance
        </p>
      </div>

      {/* Controls */}
      <div className="card p-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Currency Pair
            </label>
            <CurrencyPairSelector
              value={selectedPair}
              onChange={setSelectedPair}
              disabled={loading}
            />
          </div>
          
          <button
            onClick={loadHistory}
            disabled={loading || !selectedPair}
            className="btn btn-primary px-4 py-3 flex items-center space-x-2 mt-6"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="card p-8 text-center">
          <RefreshCw className="h-8 w-8 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading recommendation history...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="card p-6 bg-danger-50 border-danger-200">
          <p className="text-danger-800">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && selectedPair && recommendations.length === 0 && (
        <div className="card p-8 text-center">
          <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No History Found</h3>
          <p className="text-gray-600">
            No recommendations found for {selectedPair}. Try analyzing this pair first.
          </p>
        </div>
      )}

      {/* No Pair Selected */}
      {!selectedPair && !loading && (
        <div className="card p-8 text-center">
          <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Currency Pair</h3>
          <p className="text-gray-600">
            Choose a currency pair to view its recommendation history.
          </p>
        </div>
      )}

      {/* Recommendations List */}
      {!loading && recommendations.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {recommendations.length} Recommendations for {selectedPair}
            </h2>
            <div className="text-sm text-gray-500">
              Latest first
            </div>
          </div>

          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div key={rec.id || index} className="card p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-full ${getRecommendationColor(rec.recommendation)}`}>
                      {getRecommendationIcon(rec.recommendation)}
                    </div>
                    
                    <div>
                      <div className="flex items-center space-x-3">
                        <span className="text-lg font-semibold text-gray-900">
                          {rec.recommendation.toUpperCase()}
                        </span>
                        <span className={`badge ${getRecommendationColor(rec.recommendation).replace('text-', 'badge-').replace('-600', '').replace(' bg-', ' bg-')}`}>
                          {Math.round(rec.confidence_score * 100)}% confidence
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Rate: {rec.current_rate.toFixed(4)} | 
                        Trend: {rec.trend_direction || 'N/A'} | 
                        Sentiment: {rec.sentiment_score.toFixed(3)}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-sm text-gray-500">
                      {formatTimestamp(rec.created_at)}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {rec.news_count} news articles analyzed
                    </div>
                  </div>
                </div>

                {/* Technical Summary */}
                {rec.technical_summary && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <div className="text-sm font-medium text-gray-700 mb-1">Technical Analysis</div>
                    <div className="text-sm text-gray-600">{rec.technical_summary}</div>
                  </div>
                )}

                {/* Moving Averages */}
                {(rec.moving_average_5 || rec.moving_average_20 || rec.moving_average_50) && (
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    {rec.moving_average_5 && (
                      <div className="text-center">
                        <div className="text-gray-500">MA5</div>
                        <div className="font-medium">{rec.moving_average_5.toFixed(4)}</div>
                      </div>
                    )}
                    {rec.moving_average_20 && (
                      <div className="text-center">
                        <div className="text-gray-500">MA20</div>
                        <div className="font-medium">{rec.moving_average_20.toFixed(4)}</div>
                      </div>
                    )}
                    {rec.moving_average_50 && (
                      <div className="text-center">
                        <div className="text-gray-500">MA50</div>
                        <div className="font-medium">{rec.moving_average_50.toFixed(4)}</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Events */}
                {(rec.economic_events || rec.geopolitical_events) && (
                  <div className="mt-3 text-sm">
                    {rec.economic_events && (
                      <div className="mb-2">
                        <span className="font-medium text-gray-700">Economic Events: </span>
                        <span className="text-gray-600">{rec.economic_events}</span>
                      </div>
                    )}
                    {rec.geopolitical_events && (
                      <div>
                        <span className="font-medium text-gray-700">Geopolitical Events: </span>
                        <span className="text-gray-600">{rec.geopolitical_events}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default History;