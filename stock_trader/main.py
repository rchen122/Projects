import requests
from keys import key
# from file_and_graph import *
import json

def get_data(): #separate implementation because of daily API request limits
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={key}&extended_hours=true&outputsize=full'
    response = requests.get(url)
    data = response.json()

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    text = response.text
    with open("response.txt", "w") as f:
        f.write(text)
    print(data)
