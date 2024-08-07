import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt

def remove_indexes(d):
    return {key.split(' ', 1)[-1]: value for key, value in d.items()}

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            loaded_data = json.load(file)
        print("Data successfully loaded:")
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return loaded_data

# def format_csv(filename):
#     df = pd.read_csv(filename)
#     df = df.drop(index=[i for i in range(6)])
#     df.pop("Meta Data")
#     df.iloc[:, 1] = df.iloc[:, 1].apply(remove_indexes)
#     df.to_csv("edited.csv", index=False)
    
def convert_date_format(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d %H:%M")


    
def format(dict, time_interval):
    meta_data = dict["Meta Data"]
    meta_data = remove_indexes(meta_data)

    data = dict[f"Time Series ({time_interval})"]
    converted_data = {convert_date_format(key): value for key, value in data.items()}
    for _, value in converted_data.items():
        keys_to_update = list(value.keys())
        for nested_key in keys_to_update:
            value[nested_key] = float(value[nested_key])
    df = pd.DataFrame.from_dict(converted_data, orient='index')
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M")
    df = df.sort_index()
    return meta_data, df

def generate_SMA(df, length):
    df[f"SMA_{length}"] = df['4. close'].rolling(window=length).mean()
    return df

def plot_graph(df, meta_data, **kwargs):
    plt.figure(figsize=(10,6))
    keys = kwargs.keys()
    if "length" in keys:
        df = df[:][0:kwargs["length"]]
    elif "date" in keys:
        df = df[df.index.date == pd.Timestamp(kwargs["date"]).date()]
    plt.plot(df['4. close'], label="Stock Close")
    plt.plot(df["SMA_20"], label="20 SMA")
    plt.title(f"{meta_data['Symbol']} Stock Price at {meta_data['Interval']} Interval")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    data = load_json("data.json")
    meta_data, df = format(data, "5min")
    print(meta_data)
    df = generate_SMA(df, 20)
    plot_graph(df, meta_data, date="2024-08-05")
    # print(df["SMA_20"])
    # print(type(df["4. close"][0]))
