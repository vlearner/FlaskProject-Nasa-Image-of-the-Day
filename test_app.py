import unittest
from unittest.mock import patch, MagicMock
import pytest
from datetime import date
import app


class TestFlaskApp(unittest.TestCase):
    """Unit tests for the Flask NASA Image of the Day application."""
    
    def setUp(self):
        """Set up test client and application context."""
        self.app = app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
        # Reset global variable if it exists
        if hasattr(app, 'nasa_img_url'):
            delattr(app, 'nasa_img_url')
    
    def test_home_route_get(self):
        """Test the home route returns correct template and today's date."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NASA - Image of the Day', response.data)
        # Check that today's date is passed to template
        today_str = app.today
        self.assertIn(today_str.encode(), response.data)
    
    def test_imageoftheday_route_get(self):
        """Test the /imageoftheday route with GET method."""
        response = self.client.get('/imageoftheday')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NASA - Image of the Day', response.data)
    
    @patch('app.requests.Session')
    def test_imageoftheday_route_post_success(self, mock_session):
        """Test the /imageoftheday route with POST method and successful API response."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "url": "https://example.com/test-image.jpg",
            "title": "Test Image",
            "explanation": "A test image from NASA"
        }
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Test with specific date
        response = self.client.post('/imageoftheday', data={'date_pick': '2023-01-01'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NASA - Image of the Day', response.data)
        self.assertIn(b'https://example.com/test-image.jpg', response.data)
        
        # Verify the API was called with correct parameters
        mock_session_instance.get.assert_called_once()
        call_args = mock_session_instance.get.call_args
        self.assertEqual(call_args[0][0], app.base_url)
        self.assertIn('2023-01-01', call_args[1]['params'])
    
    @patch('app.requests.Session')
    def test_imageoftheday_route_post_no_date(self, mock_session):
        """Test the /imageoftheday route with POST method and no date provided."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "url": "https://example.com/today-image.jpg",
            "title": "Today's Image",
            "explanation": "Today's image from NASA"
        }
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Test without date (should use today's date)
        response = self.client.post('/imageoftheday', data={})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'https://example.com/today-image.jpg', response.data)
        
        # Verify the API was called with today's date
        mock_session_instance.get.assert_called_once()
        call_args = mock_session_instance.get.call_args
        self.assertIn(app.today, call_args[1]['params'])
    
    @patch('app.requests.Session')
    def test_imageoftheday_route_post_api_error(self, mock_session):
        """Test the /imageoftheday route when API call fails."""
        # Mock the API to raise an exception
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = Exception("API Error")
        mock_session.return_value = mock_session_instance
        
        # Test that the application handles API errors gracefully
        with self.assertRaises(Exception):
            self.client.post('/imageoftheday', data={'date_pick': '2023-01-01'})
    
    @patch('app.requests.Session')
    def test_imageoftheday_route_post_invalid_json(self, mock_session):
        """Test the /imageoftheday route when API returns invalid JSON."""
        # Mock the API to return invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Test that the application handles JSON errors gracefully
        with self.assertRaises(ValueError):
            self.client.post('/imageoftheday', data={'date_pick': '2023-01-01'})
    
    def test_app_configuration(self):
        """Test application configuration and constants."""
        self.assertTrue(hasattr(app, 'today'))
        self.assertTrue(hasattr(app, 'base_url'))
        self.assertTrue(hasattr(app, 'api_key'))
        
        # Check that today is a string representation of today's date
        self.assertEqual(app.today, str(date.today()))
        
        # Check API configuration
        self.assertEqual(app.base_url, 'https://api.nasa.gov/planetary/apod?')
        self.assertEqual(app.api_key, 'api_key=DEMO_KEY&date=')
    
    def test_flask_app_instance(self):
        """Test that Flask app is properly configured."""
        self.assertIsNotNone(app.app)
        self.assertEqual(app.app.name, 'app')


class TestFlaskAppPytest:
    """Pytest-style tests for the Flask NASA Image of the Day application."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the app."""
        app.app.config['TESTING'] = True
        with app.app.test_client() as client:
            with app.app.app_context():
                yield client
    
    def test_home_route_pytest(self, client):
        """Test the home route using pytest."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'NASA - Image of the Day' in response.data
        assert app.today.encode() in response.data
    
    def test_imageoftheday_get_pytest(self, client):
        """Test the /imageoftheday GET route using pytest."""
        response = client.get('/imageoftheday')
        assert response.status_code == 200
        assert b'NASA - Image of the Day' in response.data
    
    @patch('app.requests.Session')
    def test_imageoftheday_post_pytest(self, mock_session, client):
        """Test the /imageoftheday POST route using pytest."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"url": "https://example.com/pytest-image.jpg"}
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        response = client.post('/imageoftheday', data={'date_pick': '2023-06-01'})
        
        assert response.status_code == 200
        assert b'https://example.com/pytest-image.jpg' in response.data
        mock_session_instance.get.assert_called_once()


if __name__ == '__main__':
    # Run unittest tests
    unittest.main()