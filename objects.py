import arcpy
from arcgis.gis import GIS
from datetime import datetime, timedelta
import time
import pandas as pd


class AutoMod:

    def __init__(self):
        pass


arcpy.AddMessage("ArcGIS Online Org account")
gis = GIS('home')
arcpy.AddMessage("Logged in as " + str(gis.properties.user.username))


def get_inactive_date(days=60):
    current_time_struct = time.localtime()

    # Convert time.struct_time object to a datetime object
    current_datetime = datetime.fromtimestamp(time.mktime(current_time_struct))

    # Subtract days
    new_datetime = current_datetime - timedelta(days)

    # Convert back to time.struct_time object
    new_time_struct = new_datetime.timetuple()
    return new_time_struct


def get_inactive_users(log_csv_path: str, search_user='*'):

    import csv

    # This is an integer representing days to set the time after which a user is considered inactive.
    GRACE_PERIOD_DAYS: int = 30

    output_csv = fr'.\outputs\users_inactive_{GRACE_PERIOD_DAYS}_days_before_{str(datetime.now())[:9]}.csv'
    search_user = '*'  # change to query individual user

    # To simplify and offload authentication to the current authentication through the app, just set GIS to 'home'
    gis = GIS('home')

    user_list = gis.users.search(query=search_user, max_users=1000)

    with open(output_csv, 'w', encoding='utf-8') as file:
        csvfile = csv.writer(file, delimiter=',', lineterminator='\n')
        csvfile.writerow(
            ["Userame",  # these are the headers; modify according to whatever properties you want in your report
             "LastLogOn",
             "Name",
             ])

        for item in user_list:
            # Date math is meant to determine if the user's lastLogin attribute is < the current date minus grace period
            if item.lastLogin != -1 and time.localtime(item.lastLogin / 1000) < get_inactive_date(GRACE_PERIOD_DAYS):
                csvfile.writerow([item.username,  # modify according to whatever properties you want in your report
                                  time.strftime('%m/%d/%Y', time.localtime(item.lastLogin / 1000)),
                                  item.firstName+' '+item.lastName
                                  ])

    # This is just to print the csv to the standard out
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(output_csv, names=['Username', 'LastLogOn', 'Name'])

    for index, row in df.iterrows():
        try:
            # Access each column value using the column name
            column1_value = row['Username']
            column2_value = row['LastLogOn']
            column3_value = row['Name']

            minimum_logon_date = datetime.now() - timedelta(days=GRACE_PERIOD_DAYS)

            if datetime.strptime(column2_value, "%m/%d/%Y") < minimum_logon_date:
                print(f"Row {index + 1}: {column1_value}, {column2_value}, {column3_value}")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    get_inactive_users('')
