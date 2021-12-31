#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 15.11.2010

@author: Matthias Meißer

Harvests all user groups and generates KML files for every country

http://wiki.openstreetmap.org/wiki/Template:User_group
http://wiki.openstreetmap.org/wiki/User:UserGroupsBot
'''

# TODO
# OL linken
# Zeit einbauen
import osmwiki
import usergroups
#import zombies
from time import *
import getopt
import sys
import urllib
import re
import mykml
import sys
import os.path
import logging
import codecs
import warnings

ugroup = {}  # the parsed dictionary of the template attributes
count = 0

warnings.simplefilter(action='ignore', category=FutureWarning)


def writeStat(groups, filename):
    count = len(groups)
    recentGroups = usergroups.getNewestUserGroups(groups)
    lastGroups = u""
    for group in list(recentGroups)[0:5]:
        lastGroups = lastGroups + "," + group
    lastGroups = lastGroups[1:]
    out = codecs.open(filename, 'w+', "utf-8")
    out.write('var export_date="' +
              strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()) + '";')
    out.write('var export_number="' + str(count) + '";')
    out.write('var export_recent="' + lastGroups + '";')
    out.close()


if __name__ == '__main__':
    # init logging
    handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # parse args
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:d", [
                                   "user=", "password=", "debug"])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print("Usage: -u username -p password")
        sys.exit(2)
    user = None
    password = None
    for o, a in opts:
        if o in ("-u", "--username"):
            user = a
        elif o in ("-p", "--password"):
            password = a
        elif o in ("-d", "--debug"):
            logger.setLevel(logging.DEBUG)
    # processing
    groups = osmwiki.loadAllUserGroups(user, password)
    path, x = os.path.split(sys.argv[0])

    # save to kml
    usergroups.exportUserGroups(groups, os.path.join(
        path, "www", "osm_user_groups.kml"))
    usergroups.exportUserGroupsCountries(groups, ["DE", "AT", "CH"], os.path.join(
        path, "www", "osm_user_groups_DACH.kml"))

    # save to json
    usergroups.exportUserGroupsJSON(
        groups, os.path.join(path, "www", "osm_user_groups.json"))
    usergroups.exportUserGroupsCountriesJSON(
        groups, ["DE", "AT", "CH"], os.path.join(path, "www", "osm_user_groups_DACH.json"))

    # generate stats.js
    writeStat(groups, os.path.join(path, "www", "stat.js"))
    usergroups.saveCache(groups)
    #z=zombies.loadAllZombies(user, password)
    # filename=os.path.join(path,"www","cowboys.kml")
    #zombies.exportZombies(z, filename)
