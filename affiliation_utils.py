
import time
import pickle
import os
import csv
from difflib import SequenceMatcher
from geopy.geocoders import Nominatim
# import json

# data = json.load(open('grid.json'))
# entries = data['institutes']
# num_inst = len(entries)


def consolidated_names():
    all_ids, all_insti, all_insti_city, all_insti_country = populate_names()
    alias_ids, alias_names = populated_alias()
    labels_ids, labels_names = populate_labels()
    return all_ids, all_insti, all_insti_city, all_insti_country, alias_ids, alias_names, labels_ids, labels_names


def populate_names():
    all_ids = []
    all_insti = []
    all_insti_city = []
    all_insti_country = []
    with open('grid.csv', 'r') as h:
        reader = csv.reader(h, delimiter=',')
        for row in reader:
            all_ids.append(row[0])
            all_insti.append(row[1].lower())
            all_insti_city.append(row[2].lower())
            all_insti_country.append(row[4].lower())
    return all_ids, all_insti, all_insti_city, all_insti_country


def populated_alias():
    alias_ids = []
    alias_names = []
    with open(os.path.join('.', 'full_tables', 'aliases.csv')) as h:
        reader = csv.reader(h, delimiter=',')
        for row in reader:
            alias_ids.append(row[0].lower())
            alias_names.append(row[1].lower())
    return alias_ids, alias_names


def populate_labels():
    labels_ids = []
    labels_names = []
    with open(os.path.join('.', 'full_tables', 'labels.csv')) as h:
        reader = csv.reader(h, delimiter=',')
        for row in reader:
            labels_ids.append(row[0].lower())
            labels_names.append(row[1].lower())
    return labels_ids, labels_names


def closest_match(name_list, test_all):
    # test_all = all_insti + alias_names
    candidates = []
    for rname in name_list:
        name = rname.lower()
        s = sorted(test_all, key=lambda x: SequenceMatcher(None, x, name).ratio(), reverse=True)
        candidates.append(s[0])
        print(rname, s[0:2])
    return candidates


def fetch_text_loc(name_list):
    gids = []
    not_found = []
    candidates = []
    all_ids, all_insti, all_insti_city, all_insti_country, alias_ids, alias_names, labels_ids, labels_names = consolidated_names()
    not_found_idx = []
    for idw, rname in enumerate(name_list):
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
                    gids.append('NULL')
                    not_found_idx.append(idw)
                    not_found.append(name)

    insti_list = []
    city_list = []
    country_list = []
    for idx, gid in enumerate(gids):
        if gid != 'NULL':
            insti_list.append(all_insti[idx])
            city_list.append(all_insti_city[idx])
            country_list.append(all_insti_country[idx])
        else:
            insti_list.append('NULL')
            city_list.append('NULL')
            country_list.append('NULL')
    print(len(not_found), len(name_list))
    # if not_found:
    #     print('Not found for : ', not_found)
    #     print('Now searching for candidates')
    #     candidates = closest_match(not_found)
    #     print('Did you mean : ', candidates)
    return insti_list, city_list, country_list, not_found, not_found_idx, candidates


def fetch_loc(city_list, country_list):
    assert(len(city_list) == len(country_list))
    geolocator = Nominatim()
    locs = []
    for ii, name in enumerate(city_list):
        if ii % 20 == 0 :
            time.sleep(3)
        if name != 'NULL':
            locs.append(geolocator.geocode(name + ', ' +
                                           country_list[ii]))
            print locs[-1].longitude
        else:
            locs.append(False)
    return locs


def fetch_coauth_names(auth_list, ln_nos, email_list, co_auth):
    coauth_names = []
    email_names = []
    for ii in co_auth:
        names = []
        emails = []
        for auth_lno in ii:
            names.append(auth_list[ln_nos.index(auth_lno)])
            emails.append(email_list[ln_nos.index(auth_lno)])
        email_names.append(emails)
        coauth_names.append(names)
    return coauth_names, email_names


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
        auth_list, ln_nos, title_list, title_nos = g[0:4]
        email_list, co_auth, title_ids = g[4:7]
        auth_aff, aff_idx, abs_start_ln = g[7:10]
        coauth_names, email_names = fetch_coauth_names(auth_list, ln_nos,
                                                       email_list, co_auth)
        # year = int(this_year.rstrip('.txt'))
    # print len(auth_list), auth_list, len(auth_aff)
    return auth_aff, aff_idx, coauth_names, title_list, title_ids


auth_aff, aff_idx, coauth_names, title_list, title_ids = fetch_cosyne_affliations()  # list of list
un_resolved_list = []
for sub_list in auth_aff:
    for aff in sub_list:   # ' '.join(mystring.split())
        new = aff.strip()
        un_resolved_list.append(' '.join(new.split()))
        # print un_resolved_list[-1]
# print un_resolved_list
insti_list, city_list, country_list, not_found, not_found_idx, candidates = fetch_text_loc(un_resolved_list)
print insti_list, city_list
# for ii, noidea in enumerate(not_found):
#     print noidea, candidates[ii]
locs = fetch_loc(city_list, country_list)
lat_list = []
long_list = []

for loc in locs:
    if not loc:
        lat_list.append(loc.latitude)
        long_list.append(loc.longitude)
    else:
        lat_list.append('NULL')
        long_list.append('NULL')
print lat_list, long_list


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
