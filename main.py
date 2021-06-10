# main.py
# 2021-06-09
# Scrapes the AIS data for Innovation and writes it to a text file
# References mapping.py, which takes scraped data and writes to a map
# Scraping code from https://digital-geography.com/vessel-tracking-the-python-way/



# region Import Modules

import urllib.request
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US') # as we need to deal with names of months later on.
import os

# endregion

# region Tracked Vessels
IMOS = [9603453, 9275153, 9483413] # Set up IMO numbers for vessel tracking
IMOS_Names = ['Innovation', 'Boa Sub C', 'Furore-G'] # Identify tracked vessels

# endregion

# region AIS data scrape data from vesselfinder.com
# region AIS data scrape data from vesselfinder.com
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}
items = []
for IMO in IMOS:
    url = r'https://www.vesselfinder.com/en/vessels/VOS-TRAVELLER-IMO-' + str(IMO)
    req = urllib.request.Request(url, None, hdr)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
    parsed_html = BeautifulSoup(the_page)
    a = parsed_html.p
    tables = parsed_html.findAll("table")
    for table in tables:
        if table.findParent("table") is None:
            for row in table.findAll('tr'):
                aux = row.findAll('td')

                try:
                    if aux[0].string == "Vessel Name":
                        name = aux[1].string
                    if aux[0].string == "Position received":
                        print(aux[1].get("data-title"))
                        zeit = datetime.strptime(aux[1].get("data-title"), '%b %d, %Y %H:%M %Z')
                        print(zeit)
                except:
                    print("strange table found")
    a = parsed_html.p
    [b, c, d] = a.text.partition('nates ')
    [coords, f, g] = d.partition(')')
    coordsSplit = coords.split(" / ")


    def dms2dd(degrees, direction):
        dd = float(degrees);
        if direction == 'S' or direction == 'W':
            dd *= -1
        return dd


    def parse_dms(dms):
        parts = re.split(' ', dms)
        lat = dms2dd(parts[0], parts[1])
        return lat


    lat = parse_dms(coordsSplit[0])
    lng = parse_dms(coordsSplit[1])
    items.append((lat, lng, name, zeit))
items
# endregion

# region Write positions to .txt file
filename = 'ship_positions.txt'
if os.path.exists(filename):
    append_write = 'a' # append if already exists
    fw = open(filename,append_write)
else:
    append_write = 'w' # make a new file if not
    fw = open(filename,append_write)
    fw.write("lat;lng;name;time\n")
for item in items:
    fw.write("%3.5f;%3.5f;%s;%s\n" % item)
fw.close()
# endregion

# region Plot onto a map
from arcgis.gis import GIS
gis = GIS()
map = gis.map()
df = pd.DataFrame.from_records(items)
df.columns = ['y', 'x', 'name', 'zeit']
ships = gis.content.import_data(df)
map.add_layer(ships)
map.center = [lat, lng]
map
# endregion