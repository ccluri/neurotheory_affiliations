
import os
import csv
from difflib import SequenceMatcher
from geopy.geocoders import Nominatim
# import json

# data = json.load(open('grid.json'))
# entries = data['institutes']
# num_inst = len(entries)

all_ids = []
all_insti = []
all_insti_city = []
all_insti_country = []
alias_ids = []
alias_names = []
with open('grid.csv', 'r') as h:
    reader = csv.reader(h, delimiter=',')
    for row in reader:
        all_ids.append(row[0])
        all_insti.append(row[1].lower())
        all_insti_city.append(row[2].lower())
        all_insti_country.append(row[4].lower())
with open(os.path.join('.', 'full_tables', 'aliases.csv')) as h:
    reader = csv.reader(h, delimiter=',')
    for row in reader:
        alias_ids.append(row[0].lower())
        alias_names.append(row[1].lower())


def closest_match(name_list):
    test_all = all_insti + alias_names
    candidates = []
    for rname in name_list:
        name = rname.lower()
        s = sorted(test_all, key=lambda x: SequenceMatcher(None, x, name).ratio(), reverse=True)
        candidates = s[0:2]
    return candidates


def fetch_text_loc(name_list):
    gids = []
    not_found = []
    for rname in name_list:
        name = rname.lower()
        try:
            name_idx = all_insti.index(name)
            gids.append(all_ids[name_idx])
        except ValueError:  # check in aliases
            try:
                alias_idx = alias_names.index(name)
                gids.append(alias_ids[alias_idx])
            except ValueError:
                not_found.append(name)
    insti_list = []
    city_list = []
    country_list = []
    for gid in gids:
        idx = all_ids.index(gid)
        insti_list.append(all_insti[idx])
        city_list.append(all_insti_city[idx])
        country_list.append(all_insti_country[idx])
    if not_found:
        print('Not found for : ', not_found)
        print('Now searching for candidates')
        candidates = closest_match(not_found)
        print('Did you mean : ', candidates)
    return insti_list, city_list, country_list


def fetch_loc(city_list, country_list):
    assert(len(city_list) == len(country_list))
    geolocator = Nominatim()
    locs = []
    for ii, name in enumerate(city_list):
        locs.append(geolocator.geocode(name + ', ' +
                                       country_list[ii]))
    return locs


print(fetch_text_loc(['Oxford university',
                      'University of oxford',
                      'Caltech',
                      'New York university',
                      'the new york university']))

i, city, country = fetch_text_loc(['Cambridge University'])
locs = fetch_loc(city, country)
for loc in locs:
    print(loc.latitude, loc.longitude)
