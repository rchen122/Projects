from functions import *
from datetime import datetime
from pytz import timezone

running = True
est = str(timezone("US/Eastern"))
current_time = str(datetime.now())
hour = current_time[11:13]
minute = int(current_time[14:16])
if hour == "23":
    if 60 > minute > 30:  # upload onto google sheets at the last 30 minutes of the day
        upload_data()
        reset_intake()
        running = False


while running:
    entry = int(input("Welcome. What would you like to do?:\nLog a new food intake (1)\nAdd a new recipe (2)\n"
                      "List Daily Intake (3)\nExit (5)"))
    match entry:
        case 1:
            new_intake()
        case 2:
            add_new_recipe()
        case 3:
            list_daily_intake()
        case 4:
            list_daily_intake()
        case 5:
            running = False


