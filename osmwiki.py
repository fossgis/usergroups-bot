# -*- coding: utf-8 -*-
'''
Created on 20.06.2011

@author: Matthias Meißer
'''

from wikitools import wiki
from wikitools import api
from wikitools import pagelist
import urllib
import logging
import time

def loadAllUserGroups(user,password):
    logging.log(logging.DEBUG, "login site")
    __loginSite(user, password)
    logging.log(logging.DEBUG, "getting template list")
    templates =__getTemplatesList()
    logging.log(logging.DEBUG, "parsing templates")
    return __getUsergroups(templates)


def __loginSite(user, password):
    global site
    #connect to OSM wiki
    site = wiki.Wiki("https://wiki.openstreetmap.org/w/api.php")
    site.login(user,password)
    site.setUserAgent("UserGroupsBot 0.1")

def __getTemplatesList():
    getAllUserGroups = {'action':'query', 'list':'embeddedin',"eititle":"Template:user_group","eilimit":"500"}
    request = api.APIRequest(site, getAllUserGroups)
    return request.query()

def __getUsergroups(query):
    usergroups=[]
    list=pagelist.listFromQuery(site,query["query"]["embeddedin"])
    for page in list:
        if page.getWikiText(False).find("{{user group")>-1 : #some embedded the template within other templates so we receive fakes
            logging.log(logging.DEBUG, "request "+page.title)
            try:
                usergroup=__getTemplateAttributes(page)
                usergroups.append(usergroup)
            except Exception as e:
                logging.log(logging.ERROR, "error parsing: " + page.title + " - " + unicode(e))

    return usergroups

def __getTemplateAttributes(page):
    attrs={} #the parsed dictionary of the template attributes
    source=page.getWikiText(False).decode("utf-8") #API uses UTF-8
    source=urllib.unquote(source).replace('\n',"")
    #extract template and cut it's attributes
    start=source.find("{{user group")+len("{{user group")+1
    end=source.find("}}",start)
    source=source[start:end]
    for attr in source.split("|"):
        items=attr.split("=",1)
        if len(items)==2 : # some formatings have otherwise strange effects
            attrs[__nospaces(str(items[0]))]=__nospaces(items[1]) #remove leading linebreaks
    #assign values
    name=where=when=url=mail=wikipage=photo=country=""
    name=attrs.get("name","")
    lon=attrs.get("lon", "")
    lat=attrs.get("lat", "")
    if lon=="" or lat=="": raise Exception("no lat/lon")
    point=(lon,__nospaces(lat))
    country=attrs.get("country","")
    country=country.upper()
    state=attrs.get("state","")
    when=attrs.get("meets_when","")
    where=__expandLinks(attrs.get("meets_where",""))
    if where==None: where=""
    url=attrs.get("url","")
    if url.find(" ")>0: url=url[:url.find(" ")]
    mail=attrs.get("mailing_list_url","")
    wikipage="https://wiki.openstreetmap.org/wiki/"+page.title
    if url[-20:].replace(" ","_")==wikipage[-20:].replace(" ","_"): url=""
    photo=attrs.get("photo","")
    if not photo.isspace() and len(photo)>1 :
        #some might use additional photo formating
        if photo.find("|")>-1:
            photo=photo[:photo.find("|")]
        photo=__getImageInfos(photo) #the fotos need additional API magic
    lastedit=page.getHistory(limit=1)[0]["timestamp"]
    return {"name":name,"lonlat":point,"where":where,"when":when,"url":url,"wiki":wikipage,"mail":mail,"photo":photo,"country":country,"lastedit":lastedit}

def __nospaces(s):
    return (s.lstrip().rstrip()).replace('\n',"")

def __expandLinks(source):
    if source.find("[[")>-1:
        return __expandWikiLinks(source)
    elif source.find("[http")>-1:
        return __expandWebLinks(source)
    else: return source

def __expandWikiLinks(source):
    start=source.find("[[")
    middle=source.find("|")
    end=source.find("]]")
    if start>-1:
        temp=source[:start]
        if middle==-1:
            temp=temp+'<a href="https://wiki.openstreetmap.org/wiki/'+source[start+2:end]+'">'+source[start+2:end]+'</a>'
        else:
            temp=temp+'<a href="https://wiki.openstreetmap.org/wiki/'+source[start+2:middle]+'">'+source[middle+1:end]+'</a>'
        temp=temp+source[end+2:]
    else:
        temp=source
    return temp

def __expandWebLinks(source):
    start=source.find("[http")
    middle=source.find(" ", start)
    end=source.find("]")
    if start>-1:
        temp=source[:start]
        if middle==-1:
            temp=temp+'<a href="'+source[start+1:end]+'">'+source[start+1:end]+'</a>'
        else:
            temp=temp+'<a href="'+source[start+1:middle]+'">'+source[middle+1:end]+'</a>'
        temp=temp+source[end+1:]
    else:
        temp=source
    return temp

def __getImageInfos(name):
    global site
    if not name.isspace():
        imageURL = {'action':'query', 'prop':'imageinfo',"iiprop":"url","titles":"Image:"+name}
        time.sleep(1)
        request = api.APIRequest(site, imageURL)
        result = request.query()
        url=result["query"]["pages"].values()[0]["imageinfo"][0]["url"]
        return  url
