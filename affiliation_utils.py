
import time
import pickle
import os
import csv
# from difflib import SequenceMatcher
from geopy.geocoders import Nominatim


def consolidated_names():
    i_g_dict, g_i_dict, g_city_dict, g_country_dict = populate_names()
    alias_g_dict = populated_alias()
    labels_g_dict = populate_labels()
    output = (i_g_dict, g_i_dict, g_city_dict, g_country_dict,
              alias_g_dict, labels_g_dict)
    return output


def populate_names():
    i_g_dict = {}
    g_i_dict = {}
    g_city_dict = {}
    g_country_dict = {}
    with open('grid.csv', 'r') as h:
        reader = csv.reader(h, delimiter=',')
        for row in reader:
            i_g_dict[row[1].lower()] = row[0]
            g_i_dict[row[0]] = row[1].lower()
            g_city_dict[row[0]] = row[2].lower()
            g_country_dict[row[0]] = row[4].lower()
    return i_g_dict, g_i_dict, g_city_dict, g_country_dict


def populated_alias():
    alias_g_dict = {}
    with open(os.path.join('.', 'full_tables', 'aliases.csv')) as h:
        reader = csv.reader(h, delimiter=',')
        for row in reader:
            alias_g_dict[row[1].lower()] = row[0]
    return alias_g_dict


def populate_labels():
    labels_g_dict = {}
    with open(os.path.join('.', 'full_tables', 'labels.csv')) as h:
        reader = csv.reader(h, delimiter=',')
        for row in reader:
            labels_g_dict[row[1].lower()] = row[0]
    return labels_g_dict


def fetch_text_loc(name_list):
    gids = []
    found_idx = []
    not_found_idx = []
    i_g, g_i, g_city, g_country, a_g, l_g = consolidated_names()
    for idw, rname in enumerate(name_list):
        name = rname.lower()
        if name in i_g:
            gids.append(i_g[name])
            found_idx.append(idw)
        elif name in a_g:
            gids.append(a_g[name])
            found_idx.append(idw)
        elif name in l_g:
            gids.append(l_g[name])
            found_idx.append(idw)
        else:
            gids.append('NULL')
            not_found_idx.append(idw)
    insti_list = []
    city_list = []
    country_list = []
    for gid in gids:
        if gid != 'NULL':
            insti_list.append(g_i[gid])
            city_list.append(g_city[gid])
            country_list.append(g_country[gid])
        else:
            insti_list.append('NULL')
            city_list.append('NULL')
            country_list.append('NULL')
    print(len(not_found_idx), len(name_list))
    return gids, insti_list, city_list, country_list


def fetch_loc(city_list, country_list):
    assert(len(city_list) == len(country_list))
    geolocator = Nominatim()
    locs = []
    print('Fetching geo locations - may take some time')
    for ii, name in enumerate(city_list):
        if name != 'NULL':
            time.sleep(0.2)  # Wait for a while before request
            locs.append(geolocator.geocode(name + ', ' +
                                           country_list[ii]))
        else:
            locs.append('NULL')
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


def fetch_cosyne_affliations(this_year):
    all_abstracts = [this_year]
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
    return auth_aff, aff_idx, coauth_names, title_list, title_ids, email_names


def give_me_cosyne(this_year):
    auth_aff, aff_idx, coauth_names, title_list, title_ids, email_names = fetch_cosyne_affliations(this_year)  # list of list
    unres_aff_list = []
    title_aff_count_dict = {}
    aff_count = 0
    for title_id, title_aff_list in enumerate(auth_aff):
        title_aff_count_dict[title_id] = []
        for aff in title_aff_list:
            new = ' '.join(aff.strip().split())
            unres_aff_list.append(new)
            title_aff_count_dict[title_id].append(aff_count)
            aff_count += 1
    gids, insti_list, city_list, country_list = fetch_text_loc(unres_aff_list)
    loc_pickle = this_year.strip('.txt')+'_locs.pkl'
    redo_locs = True
    if os.path.isfile(loc_pickle):
        user = True
        while user:
            user_input = raw_input('Use existing locations? (y/n): ')
            if user_input in ['y', 'n']:
                with open(loc_pickle, 'rb') as da_file:
                    lat_list, long_list = pickle.load(da_file)
                user = False
                redo_locs = False
            elif user_input in ['n', 'N']:
                user = False
                pass
            else:
                pass
    if redo_locs:
        locs = fetch_loc(city_list, country_list)
        lat_list = []
        long_list = []
        for loc in locs:
            if loc != 'NULL':
                try:
                    lat_list.append(loc.latitude)
                    long_list.append(loc.longitude)
                except AttributeError:
                    lat_list.append('NULL')
                    long_list.append('NULL')
            else:
                lat_list.append('NULL')
                long_list.append('NULL')
        with open(loc_pickle, 'wb') as da_file:
            print('Saving locations for future reference')
            pickle.dump([lat_list, long_list], da_file, protocol=2)
    auth_count = 0
    with open(os.path.join('..', 'cosyne_analysis', 'cosyne',
                           this_year.strip('.txt') + '_aff.csv'), 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['ID', 'Email'] +
                           ['Author', 'Affiliation'] +
                           ['Aff resolved', 'GRID'] +
                           ['City', 'Country', 'Latitude', 'Longitude'])
        for idx in range(len(title_list)):
            for kk, author in enumerate(coauth_names[idx]):
                this_email = email_names[idx][kk]
                affiliations = [int(pp)-1 for pp in aff_idx[auth_count]]
                for affliation in affiliations:
                    sp_idx = title_aff_count_dict[idx][affliation]
                    csvwriter.writerow([title_ids[idx]] + [this_email] + [author] +
                                       [auth_aff[idx][affliation], insti_list[sp_idx]] +
                                       [gids[sp_idx], city_list[sp_idx], country_list[sp_idx]] +
                                       [lat_list[sp_idx], long_list[sp_idx]])
                auth_count += 1
    print('Finished :', this_year)


# all_abstracts = ['2012.txt', '2013.txt', '2014.txt',
#                  '2015.txt', '2016.txt', '2017.txt']
all_abstracts = ['2016.txt']
for abstract in all_abstracts:
    give_me_cosyne(abstract)

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
