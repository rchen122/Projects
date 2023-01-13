import json
from datetime import datetime
from endpoints import *
from googleapiclient.discovery import build
from google.oauth2 import service_account


def add_new_recipe():
    valid = False
    with open("recipes.json", mode="r") as daily_file:
        data = json.load(daily_file)
        recipe = str(input("What is the name of the new recipe: ")).lower()
        if recipe in data:
            print("Recipe is already recorded. Would you like to log an intake?")
        else:
            new_recipe = {
                recipe: {
                    "Serving Size": {
                        "amount": int(input("Serving Size: ")),
                        "units": str(input("Units (Count/Pieces/Grams): ")).lower()
                    },
                    "Calories": int(input("How many calories per serving?: ")),
                }
            }
            adding = True
            while adding:
                with open("daily_nutrition.json", mode="r") as nutrition_file:
                    nutrition_data = json.load(nutrition_file)
                    input_nutrient = str(input("Add a nutrient or type 'Done' when finished")).lower()
                    if input_nutrient in nutrition_data:
                        new_recipe[recipe][input_nutrient] = {}
                        amount = input(f"Amount in {nutrition_data[input_nutrient]['units']}: ")
                        new_recipe[recipe][input_nutrient]["amount"] = amount
                        new_recipe[recipe][input_nutrient]["units"] = nutrition_data[input_nutrient]["units"]
                    elif input_nutrient == "done":
                        adding = False
                        data.update(new_recipe)
                        valid = True
                    else:
                        print("Nutrient is not in Daily Nutrition List, try again.")
    if valid:
        with open("recipes.json", mode="w") as addition:
            json.dump(data, addition, indent=4)


def new_intake():
    with open("recipes.json", mode="r") as data_file:
        data = json.load(data_file)
        print(data)
        intake = input("What food would you like to log?: ")
        if intake not in data:
            print("We do not have the selected food in our data. Would you like to log a recipe instead?")
            return
        else:
            size = float(input(f"How many servings do you want to log? Serving size is "
                               f"{data[intake]['Serving Size']['amount']} {data[intake]['Serving Size']['units']}"))
            with open("daily_intake.json", mode="r") as log:
                existing_intake = json.load(log)
                new_entry = {
                    intake: {
                    }
                }
                for items in data[intake]:
                    if items == "Serving Size":
                        serving_size = data[intake]['Serving Size']['amount']
                        size_ratio = size / serving_size  # float
                        new_entry[intake]["Serving Sizes"] = size_ratio
                    elif items == "Calories":
                        serving_calories = data[intake]["Calories"]
                        new_entry[intake]["Calories"] = serving_calories * size_ratio
                    else:
                        new_entry[intake][items] = {}
                        new_entry[intake][items]["amount"] = data[intake][items]["amount"] * size_ratio
                        new_entry[intake][items]["units"] = data[intake][items]["units"]
                print(existing_intake)
                print(new_entry)
                existing_intake.update(new_entry)
                print(existing_intake)
            with open("daily_intake.json", mode="w") as logger:
                json.dump(existing_intake, logger, indent=4)


def list_daily_intake():
    with open("daily_intake.json", mode="r") as file:
        data = json.load(file)
        for items in data:
            if items == "PLACEHOLDER":
                pass
            else:
                print(f"{data[items]['Serving Sizes']} servings of {items}.")


def upload_data():
    sheet_input = {
        "date": datetime.now().strftime("%m/%d/%Y"),
        "calories": 0,
        "protein": 0,
        "calcium": 0,
        "fiber": 0,
        "fat": 0,
        "magnesium": 0,
        "phosphorus": 0,
        "potassium": 0,
        "vitamin a": 0,
        "vitamin b6": 0,
        "vitamin c": 0,
        "vitamin d": 0,
        "vitamin k": 0,
        "copper": 0,
        "sodium": 0,
        "zinc": 0,
        "cholesterol": 0,
        "iron": 0,
        "saturated fat": 0,
        "added sugars": 0,
        "carbohydrate": 0
    }
    with open("daily_intake.json", mode="r") as file:
        data = json.load(file)
        for items in data:
            if items == "PLACEHOLDER":
                pass
            else:
                for entry in data[items]:
                    if entry == "Serving Sizes":
                        pass
                    elif entry == "Calories":
                        sheet_input["calories"] += data[items]["Calories"]
                    else:
                        sheet_input[entry] += data[items][entry]["amount"]
    formatted_data = []
    for items in sheet_input:
        formatted_data.append(sheet_input[items])
    data1 = [formatted_data]
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets()
    sheets.values().append(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A1:V1", valueInputOption="USER_ENTERED",
                           insertDataOption="INSERT_ROWS", body={"values": data1}).execute()


def reset_intake():
    with open("daily_intake.json", mode="w") as file:
        reset = {
            "PLACEHOLDER": {}
        }
        json.dump(reset, file, indent=4)




