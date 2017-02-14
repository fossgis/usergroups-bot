#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 15.11.2010

@author: Matthias Meißer

Harvests all user groups and generates KML files for every country

http://wiki.openstreetmap.org/wiki/Template:User_group
http://wiki.openstreetmap.org/wiki/User:UserGroupsBot
'''

#TODO
#OL linken
#Zeit einbauen
import osmwiki
import usergroups
#import zombies
from time import * 
import getopt, sys
import urllib
import re
import mykml
import sys
import os.path
import logging
import codecs

ugroup={} #the parsed dictionary of the template attributes
count=0


    

def writeStat(filename,groups):
    count=len(groups)
    recentGroups=usergroups.getNewestUserGroups(groups)
    lastGroups=u""
    for group in list(recentGroups)[0:5]:
        lastGroups=lastGroups+","+group
    lastGroups=lastGroups[1:]
    out = codecs.open(filename,'w+',"utf-8");
    out.write('var export_date="'+strftime("%Y-%m-%dT %H:%M:%S UTC",gmtime())+'";')
    out.write('var export_number="'+str(count)+'";')
    out.write('var export_recent="'+lastGroups+'";')
    out.close()



if __name__ == '__main__':
    global site
    global k
    #init logging
    handler = logging.StreamHandler(sys.stdout)    
    logger = logging.getLogger() 
    logger.addHandler(handler) 
    #parse args
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:d", ["user=", "password=","debug"])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        print "Usage: -u username -p password"
        sys.exit(2)
    user = None
    password = None
    for o, a in opts:
        if o in ("-u","--username"):
            user=a
        elif o in ("-p","--password"):
            password=a
        elif o in ("-d","--debug"):
            logger.setLevel(logging.DEBUG)
    #processing
    groups=osmwiki.loadAllUserGroups(user, password)
    path,x=os.path.split(sys.argv[0])
    filename=os.path.join(path,"www","osm_user_groups.kml")
    usergroups.exportUserGroups(groups,filename)
    filename=os.path.join(path,"www","osm_user_groups_DACH.kml")
    usergroups.exportUserGroupsCountries(groups, ["DE","AT","CH"], filename)
    filename=os.path.join(path,"www","stat.js")
    writeStat(filename,groups)
    usergroups.saveCache(groups)
    #z=zombies.loadAllZombies(user, password)
    #filename=os.path.join(path,"www","cowboys.kml")
    #zombies.exportZombies(z, filename)
        
    
