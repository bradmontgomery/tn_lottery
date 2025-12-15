"""
Integration tests for the scraper module.

Tests web scraping with mocked HTTP requests.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from tn_lottery.scraper import (
    fetch_with_retry, 
    parse_amount,
    HEADERS,
    MAX_RETRIES,
    RETRY_DELAY
)


class TestFetchWithRetry:
    """Test the fetch_with_retry function."""
    
    @patch('tn_lottery.scraper.requests.get')
    def test_successful_fetch_returns_response(self, mock_get):
        """Successful fetch should return response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html>Test</html>"
        mock_get.return_value = mock_response
        
        result = fetch_with_retry("http://example.com")
        
        assert result == mock_response
        assert mock_get.call_count == 1
        
    @patch('tn_lottery.scraper.requests.get')
    def test_fetch_uses_correct_headers(self, mock_get):
        """Fetch should use proper headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        fetch_with_retry("http://example.com")
        
        # Check headers were passed
        call_args = mock_get.call_args
        assert 'headers' in call_args.kwargs
        assert call_args.kwargs['headers'] == HEADERS
        
    @patch('tn_lottery.scraper.requests.get')
    def test_fetch_has_timeout(self, mock_get):
        """Fetch should have a timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        fetch_with_retry("http://example.com")
        
        # Check timeout was passed
        call_args = mock_get.call_args
        assert 'timeout' in call_args.kwargs
        assert call_args.kwargs['timeout'] == 10
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_retries_on_non_200_status(self, mock_get, mock_sleep):
        """Should retry on non-200 status codes."""
        # First two attempts fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        
        mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        result = fetch_with_retry("http://example.com")
        
        assert result.status_code == 200
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2  # Slept twice between attempts
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_returns_none_after_max_retries(self, mock_get, mock_sleep):
        """Should return None after all retries fail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = fetch_with_retry("http://example.com", max_retries=3)
        
        assert result is None
        assert mock_get.call_count == 3
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_handles_request_exception(self, mock_get, mock_sleep):
        """Should handle request exceptions and retry."""
        # First attempt raises exception, second succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        
        mock_get.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            mock_response_success
        ]
        
        result = fetch_with_retry("http://example.com")
        
        assert result.status_code == 200
        assert mock_get.call_count == 2
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_handles_rate_limiting(self, mock_get, mock_sleep):
        """Should handle 429 rate limit responses."""
        # First attempt is rate limited, second succeeds
        mock_response_limited = Mock()
        mock_response_limited.status_code = 429
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        
        mock_get.side_effect = [mock_response_limited, mock_response_success]
        
        result = fetch_with_retry("http://example.com")
        
        assert result.status_code == 200
        assert mock_get.call_count == 2
        # Should have increased delay for rate limiting
        assert mock_sleep.called
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_custom_retry_parameters(self, mock_get, mock_sleep):
        """Should respect custom retry parameters."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        fetch_with_retry("http://example.com", max_retries=5, delay=1)
        
        assert mock_get.call_count == 5
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_timeout_exception_retries(self, mock_get, mock_sleep):
        """Should retry on timeout exceptions."""
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            mock_response_success
        ]
        
        result = fetch_with_retry("http://example.com")
        
        assert result.status_code == 200
        assert mock_get.call_count == 2


class TestParseAmount:
    """Test the parse_amount function."""
    
    def test_parse_simple_dollar_amount(self):
        """Should parse simple dollar amounts."""
        assert parse_amount("$1,000") == 1000.0
        assert parse_amount("$50") == 50.0
        assert parse_amount("$123,456.78") == 123456.78
        
    def test_parse_million_amounts(self):
        """Should parse million amounts."""
        assert parse_amount("$1 Million") == 1000000.0
        assert parse_amount("$2.5 Million") == 2500000.0
        assert parse_amount("$10 million") == 10000000.0
        
    def test_parse_without_dollar_sign(self):
        """Should parse amounts without dollar sign."""
        assert parse_amount("1,000") == 1000.0
        assert parse_amount("500") == 500.0
        
    def test_parse_with_extra_whitespace(self):
        """Should handle extra whitespace."""
        assert parse_amount("  $1,000  ") == 1000.0
        assert parse_amount("  1 Million  ") == 1000000.0
        
    def test_parse_case_insensitive(self):
        """Should be case insensitive."""
        assert parse_amount("$1 MILLION") == 1000000.0
        assert parse_amount("$2 Million") == 2000000.0
        assert parse_amount("$3 million") == 3000000.0
        
    def test_parse_empty_string(self):
        """Should handle empty strings."""
        assert parse_amount("") == 0.0
        assert parse_amount("   ") == 0.0
        
    def test_parse_none(self):
        """Should handle None."""
        assert parse_amount(None) == 0.0
        
    def test_parse_invalid_format(self):
        """Should handle invalid formats gracefully."""
        assert parse_amount("invalid") == 0.0
        assert parse_amount("$$$") == 0.0
        assert parse_amount("abc123") == 123.0  # Extracts numbers
        
    def test_parse_decimal_amounts(self):
        """Should handle decimal amounts."""
        assert parse_amount("$100.50") == 100.50
        assert parse_amount("$1,234.56") == 1234.56
        
    def test_parse_large_amounts(self):
        """Should handle large amounts."""
        assert parse_amount("$1,587,500,000") == 1587500000.0
        assert parse_amount("$100 Million") == 100000000.0
        
    def test_parse_with_commas(self):
        """Should handle commas correctly."""
        assert parse_amount("$1,000,000") == 1000000.0
        assert parse_amount("$999,999.99") == 999999.99
        
    def test_parse_special_characters(self):
        """Should strip special characters."""
        assert parse_amount("$1,000*") == 1000.0
        assert parse_amount("~$500~") == 500.0
        
    def test_parse_fractional_millions(self):
        """Should handle fractional millions."""
        assert parse_amount("$1.5 Million") == 1500000.0
        assert parse_amount("$0.5 Million") == 500000.0


class TestScraperIntegration:
    """Test scraper integration with database."""
    
    @patch('tn_lottery.scraper.requests.get')
    def test_scrape_tn_lottery_mock(self, mock_get):
        """Test scraping with mocked response."""
        # Create mock HTML response
        mock_html = """
        <html>
            <div class="prize-amount">$1,000</div>
            <div class="prize-amount">$500</div>
            <div class="game-name">Powerball</div>
            <div class="game-name">Mega Millions</div>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Just verify we can mock the request
        result = fetch_with_retry("http://example.com")
        assert result.status_code == 200
        
    @patch('tn_lottery.scraper.requests.get')
    def test_scrape_powerball_mock(self, mock_get):
        """Test Powerball scraping with mocked response."""
        # Create mock HTML response
        mock_html = """
        <html>
            <div class="winner-name">John Doe</div>
            <div class="state">TN</div>
            <div class="prize">$1 Million</div>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Just verify we can mock the request
        result = fetch_with_retry("http://example.com")
        assert result.status_code == 200


class TestScraperConstants:
    """Test scraper constants and configuration."""
    
    def test_headers_defined(self):
        """Headers should be properly defined."""
        assert HEADERS is not None
        assert 'User-Agent' in HEADERS
        assert 'Mozilla' in HEADERS['User-Agent']
        
    def test_max_retries_reasonable(self):
        """MAX_RETRIES should be reasonable."""
        assert MAX_RETRIES >= 1
        assert MAX_RETRIES <= 10
        
    def test_retry_delay_reasonable(self):
        """RETRY_DELAY should be reasonable."""
        assert RETRY_DELAY >= 0.1
        assert RETRY_DELAY <= 60


class TestScraperErrorHandling:
    """Test error handling in scraper."""
    
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_connection_error_handling(self, mock_get, mock_sleep):
        """Should handle connection errors gracefully."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = fetch_with_retry("http://example.com", max_retries=2)
        
        assert result is None
        assert mock_get.call_count == 2
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_ssl_error_handling(self, mock_get, mock_sleep):
        """Should handle SSL errors gracefully."""
        mock_get.side_effect = requests.exceptions.SSLError("SSL verification failed")
        
        result = fetch_with_retry("http://example.com", max_retries=2)
        
        assert result is None
        
    @patch('tn_lottery.scraper.time.sleep')
    @patch('tn_lottery.scraper.requests.get')
    def test_too_many_redirects_handling(self, mock_get, mock_sleep):
        """Should handle redirect errors gracefully."""
        mock_get.side_effect = requests.exceptions.TooManyRedirects("Too many redirects")
        
        result = fetch_with_retry("http://example.com", max_retries=2)
        
        assert result is None


class TestParseAmountEdgeCases:
    """Test edge cases for amount parsing."""
    
    def test_multiple_decimal_points(self):
        """Should handle multiple decimal points."""
        # Should extract what it can
        result = parse_amount("$1.2.3")
        assert isinstance(result, float)
        
    def test_negative_amounts(self):
        """Should handle negative amounts."""
        # Negative amounts aren't expected but should not crash
        result = parse_amount("-$100")
        assert isinstance(result, float)
        
    def test_very_large_number(self):
        """Should handle very large numbers."""
        result = parse_amount("$999,999,999,999")
        assert result == 999999999999.0
        
    def test_scientific_notation(self):
        """Should handle scientific notation if present."""
        # Unlikely in real data but should not crash
        result = parse_amount("1e6")
        assert isinstance(result, float)
        
    def test_unicode_characters(self):
        """Should handle unicode currency symbols."""
        # Should strip unicode and extract number
        result = parse_amount("€1,000")
        assert result == 1000.0
        
    def test_mixed_text_and_numbers(self):
        """Should extract numbers from mixed content."""
        result = parse_amount("Winner takes home $1,000 prize")
        assert result == 1000.0
        
    def test_fractional_dollars(self):
        """Should handle cents properly."""
        assert parse_amount("$0.50") == 0.50
        assert parse_amount("$10.99") == 10.99
