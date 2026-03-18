"""Additional unit tests for edge cases in sentiment analysis."""

import pytest
from app import analyze_sentiment
import random
import string

class TestSentimentEdgeCases:
    """Test edge cases for sentiment analysis."""
    
    def test_mixed_sentiment(self):
        """Test text with mixed positive and negative words."""
        text = "Gold prices are rising but market uncertainty looms"
        polarity, sentiment = analyze_sentiment(text)
        # Should be near neutral or slightly negative/positive depending on weights
        assert sentiment in ['Positive', 'Negative', 'Neutral']
        assert -1 <= polarity <= 1
    
    def test_very_long_text(self):
        """Test very long text input."""
        long_text = "Gold " * 1000 + "market analysis shows promising trends"
        polarity, sentiment = analyze_sentiment(long_text)
        assert sentiment in ['Positive', 'Negative', 'Neutral']
        assert -1 <= polarity <= 1
    
    def test_special_characters(self):
        """Test text with special characters."""
        texts = [
            "Gold!!! 🚀🚀🚀 to the moon!!!",
            "Gold??? What's happening???",
            "GOLD!! $2000/oz #investing"
        ]
        for text in texts:
            polarity, sentiment = analyze_sentiment(text)
            assert sentiment in ['Positive', 'Negative', 'Neutral']
            assert -1 <= polarity <= 1
    
    def test_multiple_languages(self):
        """Test text with multiple languages (mixed with English)."""
        text = "Gold market 黄金市场 análisis del mercado del oro"
        polarity, sentiment = analyze_sentiment(text)
        assert sentiment in ['Positive', 'Negative', 'Neutral']
    
    def test_numerical_text(self):
        """Test text with mostly numbers."""
        text = "Gold at $2000 $2010 $1995 $2020"
        polarity, sentiment = analyze_sentiment(text)
        assert sentiment in ['Positive', 'Negative', 'Neutral']
    
    def test_unicode_text(self):
        """Test text with unicode characters."""
        text = "Gold market: 📈上涨趋势 📉下跌风险"
        polarity, sentiment = analyze_sentiment(text)
        assert sentiment in ['Positive', 'Negative', 'Neutral']
    
    def test_random_string(self):
        """Test completely random string."""
        random_string = ''.join(random.choices(string.ascii_letters + string.punctuation, k=100))
        polarity, sentiment = analyze_sentiment(random_string)
        assert sentiment in ['Positive', 'Negative', 'Neutral']

class TestSentimentThresholds:
    """Test sentiment classification thresholds."""
    
    def test_boundary_values(self):
        """Test values exactly at boundaries."""
        test_cases = [
            ("Gold market exactly neutral", 0.0, 'Neutral'),
            ("Gold prices slightly positive", 0.05, 'Neutral'),  # Should be neutral (<=0.05)
            ("Gold prices slightly negative", -0.05, 'Neutral'), # Should be neutral (>= -0.05)
            ("Gold prices positive", 0.051, 'Positive'),          # Should be positive (>0.05)
            ("Gold prices negative", -0.051, 'Negative'),        # Should be negative (< -0.05)
        ]
        
        # Mock the analyzer to return specific polarity scores
        from app import analyzer
        
        # Save original method
        original_polarity_scores = analyzer.polarity_scores
        
        try:
            for text, mock_polarity, expected_sentiment in test_cases:
                # Mock the polarity_scores method
                analyzer.polarity_scores = lambda x: {'compound': mock_polarity}
                
                polarity, sentiment = analyze_sentiment(text)
                assert sentiment == expected_sentiment, f"Failed for {text} with polarity {mock_polarity}"
                assert polarity == mock_polarity
        
        finally:
            # Restore original method
            analyzer.polarity_scores = original_polarity_scores

class TestBulkSentiment:
    """Test sentiment analysis on bulk data."""
    
    def test_multiple_articles(self):
        """Test analyzing multiple articles."""
        test_articles = [
            "Gold hits all-time high as investors seek safe haven",
            "Gold prices plunge on strong dollar",
            "Gold market remains stable amid economic uncertainty",
            "Central banks increase gold reserves",
            "Gold demand drops in major markets",
            "Gold mining stocks rally on price surge",
            "Gold correction expected after recent gains"
        ]
        
        results = []
        for article in test_articles:
            polarity, sentiment = analyze_sentiment(article)
            results.append({
                'text': article,
                'polarity': polarity,
                'sentiment': sentiment
            })
        
        # Verify results
        assert len(results) == len(test_articles)
        
        # Count sentiments
        sentiment_counts = {}
        for result in results:
            sentiment_counts[result['sentiment']] = sentiment_counts.get(result['sentiment'], 0) + 1
        
        # Should have at least one of each sentiment
        assert 'Positive' in sentiment_counts
        assert 'Negative' in sentiment_counts
        assert 'Neutral' in sentiment_counts
    
    def test_consistency(self):
        """Test consistency of sentiment analysis."""
        text = "Gold prices are increasing significantly"
        
        # Analyze same text multiple times
        results = [analyze_sentiment(text) for _ in range(10)]
        
        # All results should be the same
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])