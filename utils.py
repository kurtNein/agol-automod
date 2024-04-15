"""
This file is for the AutoMod class. This class is an object responsible for fetching a local system's ArcGIS portal.
It can then perform several methods to fetch or save information from that portal.
Information available is limited to the information available to the current GIS user, handled by ArcGIS authentication.
"""



import arcpy
from arcgis.gis import GIS
from datetime import datetime, timedelta
import time
import csv


class AutoMod:
    def __init__(self):
        try:
            self.gis = GIS('home')
            self.init_message = "Logged in as " + str(self.gis.properties.user.username)
        except Exception as e:
            print(e)

        self._output_csv = ''
        self._GRACE_PERIOD_DAYS: int = 30

    def get_services_in_no_web_maps(self):
        from arcgis.mapping import WebMap

        services = (self.gis.content.search(query="", item_type="Feature Service", max_items=1000))
        total_services_queried = len(services)
        print(services, "\n", f"There are {total_services_queried} of this type")

        # creates list of items of all web maps in active portal
        web_maps = self.gis.content.search(query="", item_type="Web Map", max_items=1000)
        print(web_maps)

        # loops through list of webmap items
        for item in web_maps:
            # creates a WebMap object from input webmap item
            web_map = WebMap(item)
            # accesses basemap layer(s) in WebMap object
            base_maps = web_map.basemap['baseMapLayers']
            # accesses layers in WebMap object
            layers = web_map.layers
            # loops through basemap layers
            for bm in base_maps:
                # tests whether the bm layer has a styleUrl(VTS) or url (everything else)
                if 'styleUrl' in bm.keys():
                    for service in services:
                        if service.url in bm['styleUrl']:
                            services.remove(service)
                            print(f"Removed {service}")
                elif 'url' in bm.keys():
                    for service in services:
                        if service.url in bm['url']:
                            services.remove(service)
            # loops through layers
            for layer in layers:
                # tests whether the layer has a styleUrl(VTS) or url (everything else)
                if hasattr(layer, 'styleUrl'):
                    for service in services:
                        if service.url in layer.styleUrl:
                            services.remove(service)
                elif hasattr(layer, 'url'):
                    for service in services:
                        if service.url in layer.url:
                            services.remove(service)

        arcpy.AddMessage('The following services are not used in any web maps:')

        for service in services:
            arcpy.AddMessage(f"{service.title} : {arcpy.GetActivePortalURL() + r'home/item.html?id=' + service.id}")

        arcpy.AddMessage(f"Of {total_services_queried} services, there are {len(services)} unused in your portal")

    def get_inactive_users(self, search_user='*'):

        output_csv = fr'.\outputs\users_inactive_{self._GRACE_PERIOD_DAYS}_days_before_{str(datetime.now())[:9]}.csv'
        search_user = '*'  # change to query individual user
        self._output_csv = output_csv
        user_list = self.gis.users.search(query=search_user, max_users=1000)

        with open(output_csv, 'w', encoding='utf-8') as file:
            csvfile = csv.writer(file, delimiter=',', lineterminator='\n')
            csvfile.writerow(
                ["Username",  # these are the headers of the csv
                 "LastLogOn",
                 "Name",
                 ])

            for item in user_list:
                # Date math is to determine if the user's lastLogin attribute is < the current date minus grace period
                if item.lastLogin != -1 and time.localtime(item.lastLogin / 1000) < self.get_inactive_date():
                    csvfile.writerow([item.username,  # modify according to whatever properties you want in your report
                                      time.strftime('%m/%d/%Y', time.localtime(item.lastLogin / 1000)),
                                      item.firstName + ' ' + item.lastName
                                      ])

    def get_inactive_date(self):
        current_time_struct = time.localtime()

        # Convert time.struct_time object to a datetime object
        current_datetime = datetime.fromtimestamp(time.mktime(current_time_struct))

        # Subtract days
        new_datetime = current_datetime - timedelta(self._GRACE_PERIOD_DAYS)

        # Convert back to time.struct_time object
        new_time_struct = new_datetime.timetuple()
        return new_time_struct

    def download_items_locally(self, download_format='File Geodatabase'):
        arcpy.AddMessage("Logged in as " + str(self.gis.properties.user.username))

        try:
            # Search items by username
            items = self.gis.content.search(query='owner:*', item_type='Feature *', max_items=500)
            for item in items:
                print(item)
            print(f"Search found {len(items)} items in this portal available.")

            # Loop through each item and if equal to Feature service then download it
            for item in items:
                if item.type:
                    try:
                        print(f"Working on {item.title}...")
                        result = item.export('sample {}'.format(item.title), download_format)
                        result.download(
                            f"AGOL_{self.gis.properties.user.lastName}__{time.strftime('%m-%d-%Y', time.localtime())}")
                        print(f"Processed {item.title}")
                        # Delete the item after it downloads to save on space
                        result.delete()

                    except Exception as e:
                        print(e)
                        continue
        except Exception as e:
            print(e)


if __name__ == '__main__':
    AutoMod().download_items_locally()
