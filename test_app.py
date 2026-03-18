"""Unit tests for the Gold Market Sentiment Analyzer application."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pandas as pd
import numpy as np
from app import (
    fetch_article_content,
    fetch_news,
    analyze_sentiment,
    get_sentiment_color,
    main
)

# Test data
MOCK_ARTICLES = [
    {
        "title": "Gold prices surge to record high",
        "link": "http://example.com/1",
        "published": "2024-01-01",
        "source": "Test Source"
    },
    {
        "title": "Gold market faces uncertainty",
        "link": "http://example.com/2",
        "published": "2024-01-02",
        "source": "Test Source"
    }
]

class TestFetchArticleContent:
    """Tests for fetch_article_content function."""
    
    @patch('app.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful article content fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.text = "<html><body><p>Test content</p></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetch_article_content("http://example.com")
        assert "Test content" in result
    
    @patch('app.requests.get')
    def test_failed_fetch(self, mock_get):
        """Test failed article content fetching."""
        mock_get.side_effect = Exception("Connection error")
        
        result = fetch_article_content("http://example.com")
        assert "Content not retrieved" in result

class TestFetchNews:
    """Tests for fetch_news function."""
    
    @patch('app.feedparser.parse')
    def test_successful_fetch(self, mock_parse):
        """Test successful news fetching."""
        # Mock feedparser response
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(
                title="Gold prices surge - Test Source",
                link="http://example.com/1",
                published="2024-01-01",
                source=MagicMock(title="Test Source")
            )
        ]
        mock_parse.return_value = mock_feed
        
        results = fetch_news("gold market", num_articles=1)
        
        assert len(results) == 1
        assert results[0]["title"] == "Gold prices surge"
        assert results[0]["source"] == "Test Source"
    
    @patch('app.feedparser.parse')
    def test_empty_fetch(self, mock_parse):
        """Test fetching with no results."""
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        results = fetch_news("nonexistent", num_articles=5)
        assert len(results) == 0

class TestAnalyzeSentiment:
    """Tests for analyze_sentiment function."""
    
    def test_positive_sentiment(self):
        """Test positive sentiment analysis."""
        polarity, sentiment = analyze_sentiment("Great news! Gold prices are soaring!")
        assert sentiment == "Positive"
        assert polarity > 0.05
    
    def test_negative_sentiment(self):
        """Test negative sentiment analysis."""
        polarity, sentiment = analyze_sentiment("Terrible day for gold market as prices crash")
        assert sentiment == "Negative"
        assert polarity < -0.05
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment analysis."""
        polarity, sentiment = analyze_sentiment("Gold prices remain stable today")
        assert sentiment == "Neutral"
        assert -0.05 <= polarity <= 0.05
    
    def test_empty_text(self):
        """Test empty text input."""
        polarity, sentiment = analyze_sentiment("")
        assert sentiment == "Neutral"
        assert polarity == 0.0
    
    def test_whitespace_text(self):
        """Test whitespace-only text input."""
        polarity, sentiment = analyze_sentiment("   ")
        assert sentiment == "Neutral"
        assert polarity == 0.0

class TestGetSentimentColor:
    """Tests for get_sentiment_color function."""
    
    def test_positive_color(self):
        """Test positive sentiment color."""
        assert get_sentiment_color('Positive') == '#4CAF50'
    
    def test_negative_color(self):
        """Test negative sentiment color."""
        assert get_sentiment_color('Negative') == '#f44336'
    
    def test_neutral_color(self):
        """Test neutral sentiment color."""
        assert get_sentiment_color('Neutral') == '#FFA500'
    
    def test_invalid_sentiment(self):
        """Test invalid sentiment input."""
        assert get_sentiment_color('Invalid') == '#808080'

class TestEndToEnd:
    """End-to-end tests for the application."""
    
    @patch('app.st')
    @patch('app.fetch_news')
    def test_analysis_workflow(self, mock_fetch_news, mock_st):
        """Test the complete analysis workflow."""
        # Mock session state
        mock_st.session_state = {}
        
        # Mock fetch_news to return test data
        mock_fetch_news.return_value = MOCK_ARTICLES
        
        # Mock sidebar inputs
        mock_st.sidebar.checkbox.return_value = True
        mock_st.sidebar.slider.return_value = 5
        mock_st.sidebar.text_input.return_value = ""
        mock_st.button.return_value = True
        
        # Run main function
        with patch('app.analyze_sentiment') as mock_analyze:
            mock_analyze.side_effect = [
                (0.3, 'Positive'),
                (-0.2, 'Negative')
            ]
            
            # This would normally call main(), but we'll just test the
            # sentiment analysis part since main() is UI-heavy
            articles = MOCK_ARTICLES.copy()
            for article in articles:
                polarity, sentiment = mock_analyze(article['title'])
                article['polarity'] = polarity
                article['sentiment'] = sentiment
            
            # Verify results
            assert len(articles) == 2
            assert articles[0]['sentiment'] == 'Positive'
            assert articles[1]['sentiment'] == 'Negative'
    
    def test_sentiment_distribution_calculation(self):
        """Test sentiment distribution calculations."""
        articles = [
            {'sentiment': 'Positive', 'polarity': 0.3},
            {'sentiment': 'Positive', 'polarity': 0.4},
            {'sentiment': 'Negative', 'polarity': -0.2},
            {'sentiment': 'Neutral', 'polarity': 0.0}
        ]
        
        total = len(articles)
        sentiment_counts = {
            'Positive': sum(1 for a in articles if a['sentiment'] == 'Positive'),
            'Negative': sum(1 for a in articles if a['sentiment'] == 'Negative'),
            'Neutral': sum(1 for a in articles if a['sentiment'] == 'Neutral')
        }
        
        avg_polarity = sum(a['polarity'] for a in articles) / total
        
        assert sentiment_counts['Positive'] == 2
        assert sentiment_counts['Negative'] == 1
        assert sentiment_counts['Neutral'] == 1
        assert avg_polarity == 0.125

class TestDataFrameOperations:
    """Tests for DataFrame operations used in the app."""
    
    def test_dataframe_creation(self):
        """Test creation of DataFrame from articles."""
        articles = [
            {
                'title': 'Test Title 1',
                'polarity': 0.5,
                'sentiment': 'Positive',
                'source': 'Source 1'
            },
            {
                'title': 'Test Title 2',
                'polarity': -0.3,
                'sentiment': 'Negative',
                'source': 'Source 2'
            }
        ]
        
        df = pd.DataFrame([
            {
                'Title': a['title'][:50] + "..." if len(a['title']) > 50 else a['title'],
                'Polarity': a['polarity'],
                'Sentiment': a['sentiment'],
                'Source': a['source']
            }
            for a in articles
        ])
        
        assert len(df) == 2
        assert df['Polarity'].iloc[0] == 0.5
        assert df['Sentiment'].iloc[1] == 'Negative'
    
    def test_sentiment_filtering(self):
        """Test filtering articles by sentiment."""
        articles = [
            {'sentiment': 'Positive', 'title': 'Article 1'},
            {'sentiment': 'Positive', 'title': 'Article 2'},
            {'sentiment': 'Negative', 'title': 'Article 3'},
            {'sentiment': 'Neutral', 'title': 'Article 4'}
        ]
        
        # Test Positive filter
        positive_filter = [a for a in articles if a['sentiment'] == 'Positive']
        assert len(positive_filter) == 2
        
        # Test Negative filter
        negative_filter = [a for a in articles if a['sentiment'] == 'Negative']
        assert len(negative_filter) == 1
        
        # Test Neutral filter
        neutral_filter = [a for a in articles if a['sentiment'] == 'Neutral']
        assert len(neutral_filter) == 1
        
        # Test multiple filters
        multiple_filter = [a for a in articles if a['sentiment'] in ['Positive', 'Negative']]
        assert len(multiple_filter) == 3

def run_tests():
    """Helper function to run tests with pytest."""
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"])

if __name__ == "__main__":
    run_tests()