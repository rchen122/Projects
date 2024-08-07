import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



# Loads json file
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


# Format into pandas dataframe from python dictionary    
def format(dict, time_interval):
    meta_data = dict["Meta Data"]
    meta_data = {key.split(' ', 1)[-1]: value for key, value in meta_data.items()}

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

# Generates Simple Moving Average
def generate_SMAs(df, lengths):
    for length in lengths:
        df[f"SMA_{length}"] = df['4. close'].rolling(window=length).mean()
    return df

# Plot into pyplot
def plot_graph(df, meta_data, **kwargs):
    plt.figure(figsize=(10,6))
    keys = kwargs.keys()
    if "start_date" and "end_date" in keys:
        df = df.loc[kwargs["start_date"]:kwargs["end_date"]]
    elif "start_date" in keys:
        df = df.loc[kwargs["start_date"]:]
    elif "end_date" in keys:
        df = df.loc[:kwargs["end_date"]]
    else:
        df = df
    plt.plot(df['4. close'], label="Stock Close")
    if "SMAs" in keys:
        for SMAs in kwargs["SMAs"]:
            plt.plot(df[f"SMA_{SMAs}"], label=f"{SMAs} SMA")
    plt.title(f"{meta_data['Symbol']} Stock Price at {meta_data['Interval']} Interval")
    plt.xlabel("Date")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Set interval of ticks
    plt.gcf().autofmt_xdate()  # Rotate date labels

    plt.ylabel("Close Price")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    data = load_json("data.json") # will also be user input, need interface
    meta_data, df = format(data, "5min")
    SMAs = [20, 50] # ideally will be user input
    start_date = end_date = "2024-08-01" # user input
    df = generate_SMAs(df, SMAs)
    plot_graph(df, meta_data, start_date=start_date, end_date=end_date, SMAs=SMAs)

