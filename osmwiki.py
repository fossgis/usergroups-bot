# -*- coding: utf-8 -*-
'''
Created on 20.06.2011

@author: Matthias Meißer
'''

from wikitools3 import wiki
from wikitools3 import api
from wikitools3 import pagelist
import datetime
import logging
import urllib
import time
import re


def loadAllUserGroups(user, password):
    logging.log(logging.DEBUG, "login site")
    __loginSite(user, password)
    logging.log(logging.DEBUG, "getting template list")
    templates = __getTemplatesList()
    logging.log(logging.DEBUG, "parsing templates")
    return __getUsergroups(templates)


def __loginSite(user, password):
    global site
    # connect to OSM wiki
    site = wiki.Wiki("https://wiki.openstreetmap.org/w/api.php")
    site.setUserAgent("UserGroupsBot 0.1")
    token = site.getToken("login")
    site.login(user, password, False, False, True, "https://wiki.openstreetmap.org/w/api.php", token )


def __getTemplatesList():
    getAllUserGroups = {'action': 'query', 'list': 'embeddedin',
                        "eititle": "Template:user_group", "eilimit": "500"}
    request = api.APIRequest(site, getAllUserGroups)
    return request.query()


def __getUsergroups(query):
    today = datetime.datetime.today()
    usergroups = []
    dublicates = set()
    list = pagelist.listFromQuery(site, query["query"]["embeddedin"])
    for page in list:
        # some embedded the template within other templates so we receive fakes
        if page.getWikiText(False).find(b"{{user group") > -1:
            logging.log(logging.DEBUG, "request " + page.title)
            try:
	            usergroup = __getTemplateAttributes(page)

	            # some data quality checks, output to log
	            if usergroup["url"][-20:].replace(" ", "_") == usergroup["wiki"][-20:].replace(" ", "_"):
	                logging.info("info: " + page.title +
	                             " - " + "url is like wikiurl")
	            if usergroup["name"] == "":
	                logging.warning(
	                    "warning: " + page.title + " - " + "no name")
	            if usergroup["country"] == "":
	                logging.warning("warning: " + page.title + " - " +
	                                "no country set, so isn't in any country-filtered files (e.g. osm_user_groups_DACH.json)")
	            lastedit = datetime.datetime.strptime(
	                usergroup["lastedit"], "%Y-%m-%dT%H:%M:%SZ")
	            days = today - lastedit
	            if days.days > 365:
	                logging.info("info: " + page.title +
	                             " - " + "last edit: " + usergroup["lastedit"])
	            if usergroup["lonlat"] in dublicates:
	                logging.error("error: " + page.title +
	                              " - " + "lat/lon already used")
	            usergroups.append(usergroup)
	            dublicates.add(usergroup["lonlat"])
            except Exception as e:
                logging.log(logging.ERROR, "error: " +
                            page.title + " - " + str(e))
    return usergroups


def __getTemplateAttributes(page):
    attrs = {}  # the parsed dictionary of the template attributes
    source = page.getWikiText(False).decode("utf-8")  # API uses UTF-8
    source = urllib.request.unquote(source).replace('\n', "")

    # remove comments
    commentMatcher = re.compile("<!--.*?-->")
    source = commentMatcher.sub("", source)

    # extract template and cut it's attributes
    start = source.find("{{user group") + len("{{user group") + 1
    end = source.find("}}", start)
    source = source[start:end]
    for attr in source.split("|"):
        items = attr.split("=", 1)
        if len(items) == 2:  # some formatings have otherwise strange effects
            attrs[__nospaces(str(items[0]))] = __nospaces(
                items[1])  # remove leading linebreaks
    # assign values
    name = where = when = url = mail = wikipage = photo = country = ""
    name = attrs.get("name", "")
    lon = attrs.get("lon", "")
    lat = attrs.get("lat", "")
    if lon == "" or lat == "":
        raise Exception("no lat/lon")
    point = (lon, __nospaces(lat))
    country = attrs.get("country", "")
    country = country.upper()
    state = attrs.get("state", "")
    when = attrs.get("meets_when", "")
    where = __expandLinks(attrs.get("meets_where", ""))
    if where == None:
        where = ""
    url = attrs.get("url", "")
    if url.find(" ") > 0:
        url = url[:url.find(" ")]
    mail = attrs.get("mailing_list_url", "")
    wikipage = "https://wiki.openstreetmap.org/wiki/" + page.title
    photo = attrs.get("photo", "")
    if not photo.isspace() and len(photo) > 1:
        # some might use additional photo formating
        if photo.find("|") > -1:
            photo = photo[:photo.find("|")]
        photo = __getImageInfos(photo)  # the fotos need additional API magic
    lastedit = page.getHistory(limit=1)[0]["timestamp"]
    return {"name": name, "lonlat": point, "where": where, "when": when, "url": url, "wiki": wikipage, "mail": mail, "photo": photo, "country": country, "lastedit": lastedit}


def __nospaces(s):
    return (s.lstrip().rstrip()).replace('\n', "")


def __expandLinks(source):
    if source.find("[[") > -1:
        return __expandWikiLinks(source)
    elif source.find("[http") > -1:
        return __expandWebLinks(source)
    else:
        return source


def __expandWikiLinks(source):
    start = source.find("[[")
    middle = source.find("|")
    end = source.find("]]")
    if start > -1:
        temp = source[:start]
        if middle == -1:
            temp = temp + '<a href="https://wiki.openstreetmap.org/wiki/' + \
                source[start + 2:end] + '">' + source[start + 2:end] + '</a>'
        else:
            temp = temp + '<a href="https://wiki.openstreetmap.org/wiki/' + \
                source[start + 2:middle] + '">' + \
                source[middle + 1:end] + '</a>'
        temp = temp + source[end + 2:]
    else:
        temp = source
    return temp


def __expandWebLinks(source):
    start = source.find("[http")
    middle = source.find(" ", start)
    end = source.find("]")
    if start > -1:
        temp = source[:start]
        if middle == -1:
            temp = temp + '<a href="' + \
                source[start + 1:end] + '">' + source[start + 1:end] + '</a>'
        else:
            temp = temp + '<a href="' + \
                source[start + 1:middle] + '">' + \
                source[middle + 1:end] + '</a>'
        temp = temp + source[end + 1:]
    else:
        temp = source
    return temp


def __getImageInfos(name):
    global site
    if not name.isspace():
        imageURL = {'action': 'query', 'prop': 'imageinfo',
                    "iiprop": "url", "titles": "Image:" + name}
        time.sleep(1)
        request = api.APIRequest(site, imageURL)
        result = request.query()
        values = list(result["query"]["pages"].values())
        imageinfo = values[0]["imageinfo"]
        url = imageinfo[0]["url"]
        return url
