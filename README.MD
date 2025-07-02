To run locally

after cloning repo

cd in project folder

## Install project dependency 

### From terminal 
python3 on mac
```bash
pip3 install -r requirements.txt
```
other -
```bash
pip install -r requirements.txt
```

## **To run application** 

python3 on mac
```bash
  python3 app.py
```
 for other's -
```
python3 app.py 
```

## **To run unit tests**

Run all tests with detailed output:
```bash
python3 -m unittest test_app.py -v
```

Or use the test runner script:
```bash
python3 run_tests.py
```

Run specific test:
```bash
python3 -m unittest test_app.TestFlaskApp.test_home_route -v
```

### Test Coverage
The test suite includes 14 comprehensive unit tests covering:
- Home route functionality
- Image of the day route (GET and POST)
- NASA API integration (mocked)
- Form data handling
- Error scenarios
- Edge cases

## Running on 
##### http://127.0.0.1:5000


