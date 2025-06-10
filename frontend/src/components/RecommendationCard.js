import React from 'react';
import { TrendingUp, TrendingDown, Minus, Clock, Target, BarChart, MessageCircle, AlertTriangle } from 'lucide-react';

const RecommendationCard = ({ recommendation, loading = false }) => {
  if (loading) {
    return (
      <div className="card p-6 animate-pulse">
        <div className="space-y-4">
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="card p-6 text-center">
        <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
        <p className="text-gray-500">Select a currency pair and click "Analyze" to get started.</p>
      </div>
    );
  }

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'buy':
        return <TrendingUp className="h-6 w-6" />;
      case 'sell':
        return <TrendingDown className="h-6 w-6" />;
      default:
        return <Minus className="h-6 w-6" />;
    }
  };

  const getRecommendationColor = (type) => {
    switch (type) {
      case 'buy':
        return 'bg-success-100 text-success-800 border-success-200';
      case 'sell':
        return 'bg-danger-100 text-danger-800 border-danger-200';
      default:
        return 'bg-warning-100 text-warning-800 border-warning-200';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-success-600';
    if (confidence >= 0.6) return 'text-warning-600';
    return 'text-danger-600';
  };

  return (
    <div className="card p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-lg border-2 ${getRecommendationColor(recommendation.recommendation)}`}>
            {getRecommendationIcon(recommendation.recommendation)}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {recommendation.recommendation.toUpperCase()}
            </h2>
            <p className="text-gray-500">{recommendation.currency_pair}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">
            {recommendation.current_rate.toFixed(4)}
          </div>
          <div className={`text-sm font-medium ${getConfidenceColor(recommendation.confidence_score)}`}>
            {Math.round(recommendation.confidence_score * 100)}% Confidence
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <BarChart className="h-5 w-5 text-gray-600 mx-auto mb-2" />
          <div className="text-sm text-gray-600">Technical</div>
          <div className="font-semibold text-gray-900">
            {recommendation.technical_analysis.trend_direction || 'Neutral'}
          </div>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <MessageCircle className="h-5 w-5 text-gray-600 mx-auto mb-2" />
          <div className="text-sm text-gray-600">Sentiment</div>
          <div className="font-semibold text-gray-900">
            {recommendation.sentiment_analysis.score > 0.1 ? 'Positive' : 
             recommendation.sentiment_analysis.score < -0.1 ? 'Negative' : 'Neutral'}
          </div>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <AlertTriangle className="h-5 w-5 text-gray-600 mx-auto mb-2" />
          <div className="text-sm text-gray-600">News</div>
          <div className="font-semibold text-gray-900">
            {recommendation.sentiment_analysis.news_count} Articles
          </div>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Clock className="h-5 w-5 mr-2" />
          Analysis Details
        </h3>
        
        {/* Technical Analysis */}
        <div className="border-l-4 border-primary-400 pl-4">
          <h4 className="font-medium text-gray-900 mb-2">Technical Analysis</h4>
          <div className="text-sm text-gray-600 space-y-1">
            <div className="grid grid-cols-2 gap-4">
              {recommendation.technical_analysis.moving_average_5 && (
                <div>
                  <span className="font-medium">MA5:</span> {recommendation.technical_analysis.moving_average_5.toFixed(4)}
                </div>
              )}
              {recommendation.technical_analysis.moving_average_20 && (
                <div>
                  <span className="font-medium">MA20:</span> {recommendation.technical_analysis.moving_average_20.toFixed(4)}
                </div>
              )}
            </div>
            <p className="mt-2">{recommendation.technical_analysis.summary}</p>
          </div>
        </div>

        {/* Sentiment Analysis */}
        <div className="border-l-4 border-blue-400 pl-4">
          <h4 className="font-medium text-gray-900 mb-2">Market Sentiment</h4>
          <div className="text-sm text-gray-600">
            <div className="flex items-center justify-between mb-2">
              <span>Sentiment Score:</span>
              <span className={`font-medium ${
                recommendation.sentiment_analysis.score > 0 ? 'text-success-600' : 
                recommendation.sentiment_analysis.score < 0 ? 'text-danger-600' : 'text-gray-600'
              }`}>
                {recommendation.sentiment_analysis.score.toFixed(3)}
              </span>
            </div>
            <p>{recommendation.sentiment_analysis.summary}</p>
          </div>
        </div>

        {/* Event Analysis */}
        {(recommendation.event_analysis.economic_events || recommendation.event_analysis.geopolitical_events) && (
          <div className="border-l-4 border-orange-400 pl-4">
            <h4 className="font-medium text-gray-900 mb-2">Market Events</h4>
            <div className="text-sm text-gray-600 space-y-2">
              {recommendation.event_analysis.economic_events && (
                <div>
                  <span className="font-medium">Economic:</span>
                  <p className="mt-1">{recommendation.event_analysis.economic_events}</p>
                </div>
              )}
              {recommendation.event_analysis.geopolitical_events && (
                <div>
                  <span className="font-medium">Geopolitical:</span>
                  <p className="mt-1">{recommendation.event_analysis.geopolitical_events}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Justification */}
      <div className="border-t pt-4">
        <h4 className="font-medium text-gray-900 mb-3">AI Justification</h4>
        <div className="bg-gray-50 rounded-lg p-4">
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
            {recommendation.justification}
          </pre>
        </div>
      </div>

      {/* Timestamp */}
      <div className="text-xs text-gray-500 text-center border-t pt-2">
        Analysis generated at {new Date(recommendation.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default RecommendationCard;