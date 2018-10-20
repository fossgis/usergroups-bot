#!/usr/bin/python
# -*- coding: utf-8 -*-

import geojson
import io
import json
import logging
import mf2py
import os.path
import sys

eventsurl = "https://wiki.openstreetmap.org/w/index.php?title=User:Haribo/Calendar&printable=yes"

features = []

events = mf2py.parse(url=eventsurl)
for event in events["items"]:
    properties = event["properties"]
    try:
        name, place, country = properties["name"][0].split(',')
        properties["name"] = name
        properties["locality"] = place
        properties["country"] = country
    except:
        split = True
    children = event["children"]
    for child in children:
        lat = float(child["properties"]["latitude"][0])
        lon = float(child["properties"]["longitude"][0])
        try:
            properties["locality"] = child["properties"]["locality"][0]
            properties["country"] = child["properties"]["country"][0]
        except:
            split = False
    features.append(geojson.Feature(
        geometry=geojson.Point((lon, lat)), properties=properties))

collection = geojson.FeatureCollection(features)
print geojson.dumps(collection, indent=2, separators=(',', ':'))
