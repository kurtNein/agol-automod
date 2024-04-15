"""
This is an automatic moderation tool, or AutoMod, designed to gather information about an ArcGIS Online organization.
The intent is to automate querying things like users or content to inform certain decisions.
The AutoMod authenticates through arcgis module, and should minimize additional auth methods exposed.
"""

from utils import AutoMod


def main():
    am = AutoMod()
    am.get_inactive_users()
    am.get_services_in_no_web_maps()


if __name__ == '__main__':
    main()
