import requests
from keys import key
from file_and_graph import *
from algos import *
import json
from itertools import combinations

def get_data(): #separate implementation because of daily API request limits
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={key}&extended_hours=true&outputsize=full'
    response = requests.get(url)
    data = response.json()

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    text = response.text
    with open("response.txt", "w") as f:
        f.write(text)

if __name__ == "__main__":
    # get_data()
    data = load_json("data.json") # will also be user input, need interface
    meta_data, df = format(data, "5min")
    SMA_range = np.arange(8, 50)
    combos = combinations(SMA_range, 2)
    target = 2.3
    risk = 2
    df = generate_SMAs(df, SMA_range)
    SMAs = [15, 46] # [18,43] [16, 27] [15 46]
    profits = np.array([])
    for date, group, in df.groupby(df.index.date):
        profit, entry_time, entry_price, exit_time, exit_price= SMA_crossing(date, group, SMAs, target, risk)
        profits = np.append(profits, profit)
        print("Date: {}, Profit: {}, Entry Time: {}, Entry Price: {}, Exit Time: {}, Exit Price: {}".format(date, profit, entry_time, entry_price, exit_time, exit_price))

        

    plot_graph(df, meta_data, start_date="2024-08-14", SMAs=SMAs)

    
    print(profits)
    print(sum(profits>0)/len(profits), sum(profits<0)/len(profits))
    print(np.mean(profits), np.sum(profits))
