# [UserGroupsBot](https://wiki.openstreetmap.org/wiki/User:UserGroupsBot)

This is a bot written in Python 2 and updated to Python 3, collecting all [Template:User_group](https://wiki.openstreetmap.org/wiki/Template:User_group) together
and generating [KML](https://wiki.openstreetmap.org/wiki/KML) and [GeoJSON](https://wiki.openstreetmap.org/wiki/GeoJSON) files to show them on a map: http://usergroups.openstreetmap.de

## Python setup

You need to install the packages and `geojson` via pip3:

```sh
pip3 install geojson
```

> Originally the `wikitools` module was used, but neither the original Python3 branch nor the fork from https://github.com/elsiehupp/wikitools3 works properly. Therefore an adapted wikitools3 is supplied directly.


Also a local HTTP server might be helpful in order to locally run the web app.

## Run the bot

Just execute `python3 wiki2users.py -u <you-wiki-username> -p <your-wiki-password>` to run the bot. This takes a moment and generates the `.json` and `.kml` files wihtin the `www` folder.

## Run the web app

Just start a local http-server within the `www` directory (e.g. using the npm package `http-server`: `http-server -p 8000 --cors='*'`).
