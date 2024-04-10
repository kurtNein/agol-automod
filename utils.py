import arcpy
from arcgis.gis import GIS
from datetime import datetime, timedelta
import time


class AutoMod:
    def __init__(self):
        try:
            self.gis = GIS('home')
            self.init_message = "Logged in as " + str(self.gis.properties.user.username)
        except Exception as e:
            print(e)

        self._output_csv = ''
        self._GRACE_PERIOD_DAYS: int = 30

    def get_inactive_users(self, search_user='*'):
        import csv

        # This is an integer representing days to set the time after which a user is considered inactive.

        output_csv = fr'.\outputs\users_inactive_{self._GRACE_PERIOD_DAYS}_days_before_{str(datetime.now())[:9]}.csv'
        search_user = '*'  # change to query individual user
        self._output_csv = output_csv
        user_list = self.gis.users.search(query=search_user, max_users=1000)

        with open(output_csv, 'w', encoding='utf-8') as file:
            csvfile = csv.writer(file, delimiter=',', lineterminator='\n')
            csvfile.writerow(
                ["Userame",  # these are the headers; modify according to whatever properties you want in your report
                 "LastLogOn",
                 "Name",
                 ])

            for item in user_list:
                # Date math is to determine if the user's lastLogin attribute is < the current date minus grace period
                if item.lastLogin != -1 and time.localtime(item.lastLogin / 1000) < self.get_inactive_date(
                        self._GRACE_PERIOD_DAYS):
                    csvfile.writerow([item.username,  # modify according to whatever properties you want in your report
                                      time.strftime('%m/%d/%Y', time.localtime(item.lastLogin / 1000)),
                                      item.firstName + ' ' + item.lastName
                                      ])

    def get_inactive_date(self, days=60):
        current_time_struct = time.localtime()

        # Convert time.struct_time object to a datetime object
        current_datetime = datetime.fromtimestamp(time.mktime(current_time_struct))

        # Subtract days
        new_datetime = current_datetime - timedelta(days)

        # Convert back to time.struct_time object
        new_time_struct = new_datetime.timetuple()
        return new_time_struct


if __name__ == '__main__':
    AutoMod().get_inactive_users()
