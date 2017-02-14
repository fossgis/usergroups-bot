'''
Created on 10.01.2012

@author: g
just for Operation Cowboy
'''

from wikitools import wiki
from wikitools import api
from wikitools import pagelist
import mykml
import urllib
import logging

def loadAllZombies(user,password):
    logging.log(logging.DEBUG, "login site") 
    __loginSite(user, password)
    logging.log(logging.DEBUG, "getting template list")
    templates =__getTemplatesList()
    logging.log(logging.DEBUG, "parsing templates")
    return __getZombies(templates)

def __loginSite(user, password):
    global site
    #connect to OSM wiki
    site = wiki.Wiki("http://wiki.openstreetmap.org/w/api.php")
    site.login(user,password)
    site.setUserAgent("UserGroupsBot 0.1")
    
def __getTemplatesList():
    getAllUserGroups = {'action':'query', 'list':'embeddedin',"eititle":"Template:operation_cowboy","eilimit":"500"}
    request = api.APIRequest(site, getAllUserGroups)
    return request.query()

def __getZombies(query):
    usergroups=[]
    list=pagelist.listFromQuery(site,query["query"]["embeddedin"])
    for page in list:
        logging.log(logging.DEBUG, "request "+page.title)
        try:
            usergroup=__getTemplateAttributes(page)
            usergroups.append(usergroup)
        except:
            logging.log(logging.ERROR, "error parsing: "+page.title)
    return usergroups
                
def __getTemplateAttributes(page):
    attrs={} #the parsed dictionary of the template attributes 
    source=page.getWikiText(False).decode("utf-8") #API uses UTF-8
    source=urllib.unquote(source).replace('\n',"")
    #extract template and cut it's attributes
    start=source.find("{{operation cowboy")+len("{{operation cowboy")+1
    end=source.find("}}",start)
    source=source[start:end]
    for attr in source.split("|"):
        items=attr.split("=",1)                
        if len(items)==2 : # some formatings have otherwise strange effects
            attrs[__nospaces(str(items[0]))]=__nospaces(items[1]) #remove leading linebreaks
    #assign values
    name=where=when=lon=lat=notes=""
    name=attrs.get("name","")
    point=(attrs["lon"]),__nospaces(attrs["lat"])
    when=attrs.get("when","")
    where=__expandLinks(attrs.get("where",""))
    if where==None: where=""
    when=attrs.get("notes","")
    wikipage="http://wiki.openstreetmap.org/wiki/"+page.title
    return {"name":name,"lonlat":point,"where":where,"when":when,"wiki":wikipage,"notes":notes}

def __nospaces(s):
    return (s.lstrip().rstrip()).replace('\n',"") 

def __expandLinks(source):
    if source.find("[[")>-1: __expandWikiLinks(source)
    if source.find("[http")>-1: __expandWebLinks(source)
    
def __expandWikiLinks(source):
    start=source.find("[[")
    middle=source.find("|")
    end=source.find("]]")
    if start>-1:
        temp=source[:start]
        if middle==-1:
            temp=temp+'<a href="https://wiki.osm.org/wiki/'+source[start+2:end]+'">'+source[start+2:end]+'</a>'
        else:
            temp=temp+'<a href="https://wiki.osm.org/wiki/'+source[start+2:middle]+'">'+source[middle+1:end]+" ("+source[start+2+len("Benutzer:"):middle]+")"+'</a>'
        temp=temp+source[end+2:]
    else:
        temp=source
    return temp

def __expandWebLinks(source):
    start=source.find("[http")
    middle=source.find(" ")
    end=source.find("]")
    if start>-1:
        temp=source[:start]
        if middle==-1:
            temp=temp+'<a href="https://wiki.opennet-initiative.de/wiki/'+source[start+2:end]+'">'+source[start+2:end]+'</a>'
        else:
            temp=temp+'<a href="https://wiki.opennet-initiative.de/wiki/'+source[start+2:middle]+'">'+source[middle+1:end]+" ("+source[start+2+len("Benutzer:"):middle]+")"+'</a>'
        temp=temp+source[end+2:]
    else:
        temp=source
    return temp

def exportZombies(groups,filename):
    #create a KML
    k=mykml.kml("OSM Operation cowboy","Generated list of local Mapping parties by UserGroupsBot")
    k.add_style("usergroup","boots.png")   
    #save groups
    for ugroup in groups:
        point=ugroup["lonlat"]
        name=ugroup["name"]
        rest=ugroup.copy();
        del rest["lonlat"]
        del rest["name"]   
        k.add_placemark(name,point,"usergroup",rest)
    k.save(filename)
