# Forex Trading Advisor

A full-stack application that provides forex trading recommendations based on technical analysis, sentiment analysis, and macroeconomic events.

## Features

- Live forex rate analysis using Alpha Vantage API
- Real-time news sentiment analysis
- Macroeconomic and geopolitical event detection
- Buy/Hold/Sell recommendations with detailed justifications
- React frontend with Tailwind CSS
- Python FastAPI backend
- SQLite database for logging decisions

## Project Structure

```
forex-strategist/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Configuration and settings
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic modules
│   │   └── utils/        # Utility functions
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API integration
│   │   └── utils/        # Utility functions
│   ├── public/
│   └── package.json
└── .env.example
```

## Quick Start

### Option 1: Using Python Runners (Recommended)

**Backend:**
```bash
python run_backend.py
```

**Frontend:**
```bash
python run_frontend.py
```

### Option 2: Manual Setup

**Backend:**
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Copy `.env.example` to `.env` and configure API keys
5. Run: `cd backend && uvicorn app.main:app --reload`

**Frontend:**
1. Install dependencies: `cd frontend && npm install`
2. Start development server: `npm start`

## API Keys Setup

Get your free API keys:

1. **Alpha Vantage API** (Required)
   - Visit: https://www.alphavantage.co/support/#api-key
   - Sign up for free API key
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

2. **News API** (Optional - RSS feeds used as fallback)
   - Visit: https://newsapi.org/register
   - Get free API key (500 requests/day)
   - Add to `.env`: `NEWS_API_KEY=your_key_here`

## Features

- **Real-time Forex Analysis**: Live rates and technical indicators
- **Sentiment Analysis**: News sentiment from multiple sources
- **Event Detection**: Macroeconomic and geopolitical events
- **AI Recommendations**: Buy/Hold/Sell with confidence scores
- **Historical Tracking**: View past recommendations
- **Clean UI**: Modern React interface with Tailwind CSS

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/analyze` - Analyze currency pair
- `GET /api/v1/rates/{pair}` - Get current exchange rate
- `GET /api/v1/news/{pair}` - Get recent news
- `GET /api/v1/history/{pair}` - Get recommendation history
- `GET /api/v1/supported-pairs` - List supported pairs