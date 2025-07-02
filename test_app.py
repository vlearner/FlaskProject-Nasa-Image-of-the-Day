import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import date
import app


class TestFlaskApp(unittest.TestCase):
    """Unit tests for the Flask NASA Image of the Day application."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Sample NASA API response for testing
        self.sample_nasa_response = {
            "url": "https://apod.nasa.gov/apod/image/test_image.jpg",
            "title": "Test Astronomy Picture",
            "explanation": "This is a test image from NASA's APOD API"
        }
    
    def tearDown(self):
        """Clean up after each test method."""
        self.app_context.pop()
        # Reset global variable
        app.nasa_img_url = None
    
    def test_home_route(self):
        """Test the home route ('/') returns correct response."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NASA - Image of the Day', response.data)
        # Check that today's date is passed to template
        today_str = str(date.today())
        self.assertIn(today_str.encode(), response.data)
    
    def test_imageoftheday_get_request(self):
        """Test GET request to /imageoftheday route."""
        response = self.client.get('/imageoftheday')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NASA - Image of the Day', response.data)
    
    def test_imageoftheday_get_with_existing_url(self):
        """Test GET request when nasa_img_url is already set."""
        # Set global variable
        app.nasa_img_url = "https://test-image-url.jpg"
        
        response = self.client.get('/imageoftheday')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'https://test-image-url.jpg', response.data)
    
    @patch('app.requests.Session')
    def test_imageoftheday_post_request_with_date(self, mock_session):
        """Test POST request to /imageoftheday with a specific date."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_nasa_response
        mock_session.return_value.get.return_value = mock_response
        
        # Test data
        test_date = "2023-12-25"
        form_data = {'date_pick': test_date}
        
        response = self.client.post('/imageoftheday', data=form_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.sample_nasa_response["url"].encode(), response.data)
        
        # Verify API was called with correct parameters
        mock_session.return_value.get.assert_called_once()
        call_args = mock_session.return_value.get.call_args
        self.assertEqual(call_args[0][0], app.base_url)  # First positional argument (URL)
        self.assertIn('api_key=DEMO_KEY&date=' + test_date, call_args[1]['params'])  # params keyword argument
        
        # Verify global variable was set
        self.assertEqual(app.nasa_img_url, self.sample_nasa_response["url"])
    
    @patch('app.requests.Session')
    def test_imageoftheday_post_request_without_date(self, mock_session):
        """Test POST request to /imageoftheday without date (should use today)."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_nasa_response
        mock_session.return_value.get.return_value = mock_response
        
        # Empty form data (no date_pick)
        form_data = {}
        
        response = self.client.post('/imageoftheday', data=form_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.sample_nasa_response["url"].encode(), response.data)
        
        # Verify API was called with today's date
        mock_session.return_value.get.assert_called_once()
        call_args = mock_session.return_value.get.call_args
        expected_date = str(date.today())
        self.assertIn('api_key=DEMO_KEY&date=' + expected_date, call_args[1]['params'])
    
    @patch('app.requests.Session')
    def test_imageoftheday_post_request_with_empty_date(self, mock_session):
        """Test POST request with empty date string."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_nasa_response
        mock_session.return_value.get.return_value = mock_response
        
        # Form data with empty date
        form_data = {'date_pick': ''}
        
        response = self.client.post('/imageoftheday', data=form_data)
        
        # Current behavior: empty string is passed as-is (not converted to today's date)
        self.assertEqual(response.status_code, 200)
        call_args = mock_session.return_value.get.call_args
        # With empty string, the API parameter becomes 'api_key=DEMO_KEY&date='
        self.assertIn('api_key=DEMO_KEY&date=', call_args[1]['params'])
    
    @patch('app.requests.Session')
    def test_api_request_headers(self, mock_session):
        """Test that API requests include proper headers."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_nasa_response
        mock_session.return_value.get.return_value = mock_response
        
        form_data = {'date_pick': '2023-01-01'}
        
        self.client.post('/imageoftheday', data=form_data)
        
        # Verify headers were set correctly
        call_args = mock_session.return_value.get.call_args
        self.assertEqual(call_args[1]['headers']['User-Agent'], 'Mozilla/5.0')
    
    @patch('app.requests.Session')
    def test_nasa_api_error_handling(self, mock_session):
        """Test handling of NASA API errors."""
        # Mock an API error
        mock_session.return_value.get.side_effect = Exception("API Error")
        
        form_data = {'date_pick': '2023-01-01'}
        
        # This should raise an exception since there's no error handling in the original code
        with self.assertRaises(Exception):
            self.client.post('/imageoftheday', data=form_data)
    
    @patch('app.requests.Session')
    def test_nasa_api_invalid_json_response(self, mock_session):
        """Test handling of invalid JSON response from NASA API."""
        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_session.return_value.get.return_value = mock_response
        
        form_data = {'date_pick': '2023-01-01'}
        
        # This should raise an exception since there's no error handling
        with self.assertRaises(json.JSONDecodeError):
            self.client.post('/imageoftheday', data=form_data)
    
    @patch('app.requests.Session')
    def test_nasa_api_missing_url_key(self, mock_session):
        """Test handling when NASA API response doesn't contain 'url' key."""
        # Mock response without 'url' key
        mock_response = MagicMock()
        mock_response.json.return_value = {"title": "Test", "explanation": "Test explanation"}
        mock_session.return_value.get.return_value = mock_response
        
        form_data = {'date_pick': '2023-01-01'}
        
        # This should raise a KeyError since there's no error handling
        with self.assertRaises(KeyError):
            self.client.post('/imageoftheday', data=form_data)
    
    def test_global_variable_initialization(self):
        """Test that global variable is properly initialized."""
        # Import fresh copy to test initialization
        import importlib
        importlib.reload(app)
        
        self.assertIsNone(app.nasa_img_url)
    
    def test_constants_are_set_correctly(self):
        """Test that application constants are set correctly."""
        self.assertTrue(app.base_url.startswith('https://api.nasa.gov'))
        self.assertIn('DEMO_KEY', app.api_key)
        self.assertEqual(app.today, str(date.today()))
    
    def test_flask_app_configuration(self):
        """Test Flask app basic configuration."""
        self.assertEqual(app.app.name, 'app')
        # Verify routes are registered
        routes = [rule.rule for rule in app.app.url_map.iter_rules()]
        self.assertIn('/', routes)
        self.assertIn('/imageoftheday', routes)
    
    def test_template_context(self):
        """Test that templates receive correct context variables."""
        response = self.client.get('/')
        # Check that response contains template content (basic check)
        self.assertIn(b'Choose a Day', response.data)
        self.assertIn(b'form', response.data)


if __name__ == '__main__':
    unittest.main()