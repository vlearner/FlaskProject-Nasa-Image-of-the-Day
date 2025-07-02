To run locally

after cloning repo

cd in project folder

##Install project dependency 

###From terminal 
python3 on mac
```bash
pip3 install -r requirements.txt
```
other -
```bash
pip install -r requirements.txt
```

##**To run application** 

python3 on mac
```bash
  python3 app.py
```
 for other's -
```
python3 app.py 
```


##Running on 
#####http://127.0.0.1:5000

## **Running Tests**

The project includes comprehensive unit tests for the Flask application.

### To run tests with pytest:
```bash
pytest test_app.py -v
```

### To run tests with unittest:
```bash
python -m unittest test_app.py -v
```

### Test Coverage:
- Home page route testing
- Image of the day route testing (GET and POST)
- NASA API mocking to avoid external dependencies
- Error handling scenarios
- Application configuration validation


