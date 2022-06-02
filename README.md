# fuel_checker
Telegram bot for observing fuel availability on WOG fuel stations.

# How to install (on Windows for Python 3):
1. Clone repository
2. Open command prompt in root folder
3. Create virtual environment (venv) for this project:
```
python -m venv venv
```
4. Activate venv:
```
call ./venv/Scripts/activate
```
5. Install requirements:
```
pip install -r requirements.txt
```


# How to run:
1. Create a telegram bot and get a token
2. Copy the token to the python file `parse_wog.py`
3. Replace WOG fuel station IDs
4. Execute
```
python parse_wog.py
```
5. Ask bot to /start
