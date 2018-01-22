
import pickle
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
labels_ids = []
labels_names = []
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
with open(os.path.join('.', 'full_tables', 'labels.csv')) as h:
    reader = csv.reader(h, delimiter=',')
    for row in reader:
        labels_ids.append(row[0].lower())
        labels_names.append(row[1].lower())


def closest_match(name_list):
    test_all = all_insti + alias_names
    candidates = []
    for rname in name_list:
        name = rname.lower()
        s = sorted(test_all, key=lambda x: SequenceMatcher(None, x, name).ratio(), reverse=True)
        candidates.append(s[0])
    return candidates


def fetch_text_loc(name_list):
    gids = []
    not_found = []
    candidates = []
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
                try:
                    labels_idx = labels_names.index(name)
                    gids.append(labels_ids[labels_idx])
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
    print(len(not_found), len(name_list), name_list)
    if not_found:
        print('Not found for : ', not_found)
        print('Now searching for candidates')
        candidates = closest_match(not_found)
        print('Did you mean : ', candidates)
    return insti_list, city_list, country_list, not_found, candidates


def fetch_loc(city_list, country_list):
    assert(len(city_list) == len(country_list))
    geolocator = Nominatim()
    locs = []
    for ii, name in enumerate(city_list):
        locs.append(geolocator.geocode(name + ', ' +
                                       country_list[ii]))
    return locs


def fetch_cosyne_affliations():
    # all_abstracts = ['2012.txt', '2013.txt', '2014.txt',
    #                  '2015.txt', '2016.txt', '2017.txt']
    all_abstracts = ['2013.txt']

    big_list = {}
    for this_year in all_abstracts:
        with open(os.path.join('..', 'cosyne_analysis', 'cosyne',
                               this_year+'_meta.pkl'), 'rb') as da_file:
            big_list[this_year] = pickle.load(da_file)
    for this_year in all_abstracts:
        g = big_list[this_year]
        auth_aff, aff_idx = g[7:9]
        # year = int(this_year.rstrip('.txt'))
    return auth_aff, aff_idx


def gen_name_exceptions(un_resolved_list):
    f_names = []
    for a_name in un_resolved_list:
        name = a_name.lower()
        if name.find('universitycollege') != -1:
            f_names.append(name.replace('universitycollege', 'university college'))
        elif name.find('universityof') != -1:
            f_names.append(name.replace('universityof', 'university of'))
        elif name.find('brandeisuniversity') != -1:
            f_names.append(name.replace('brandeisuniversity', 'brandeis university'))
        elif name.find('yaleuniversity') != -1:
            f_names.append(name.replace('yaleuniversity', 'yale university'))
        elif name.find('baylorcollege') != -1:
            f_names.append(name.replace('baylorcollege', 'baylor college'))
        else:
            f_names.append(name)
    return f_names


auth_aff, aff_idx = fetch_cosyne_affliations()  # list of list
un_resolved_list = []
for sub_list in auth_aff:
    for aff in sub_list:   # ' '.join(mystring.split())
        new = aff.strip()
        un_resolved_list.append(' '.join(new.split()))
        # print un_resolved_list[-1]
# print un_resolved_list
f_names = gen_name_exceptions(un_resolved_list)
insti_list, city_list, country_list, not_found, candidates = fetch_text_loc(f_names)
# print not_found, candidates



# i, city, country = fetch_text_loc(['Oxford university',
#                                    'University of oxford',
#                                    'Caltech',
#                                    'New York university',
#                                    'the new york university'])

# i, city, country = fetch_text_loc(['Cambridge University'])
# locs = fetch_loc(city, country)
# for loc in locs:
#     print city, country
#     print(loc.latitude, loc.longitude)
