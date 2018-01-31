import readline
import affiliation_utils as utils
import csv
import os
import bing


class MyCompleter(object):  # Custom completer
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                if text in s]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


def victor_newfile(filename='authorsUnresolvedAff.csv', new_filename='authorsResolvedAff.csv'):
    name_exceptions = utils.exceptions_alias()
    year_list, title_list, author_list, aff_list, email_list = victor_exceptions(filename)
    i_g, g_i, g_city, g_country, a_g, l_g = utils.consolidated_names()
    gid_list = []
    city_list = []
    country_list = []
    for raff in aff_list:
        aff = raff.lower()
        if aff in name_exceptions.keys():
            new_gid = utils.resolve_name(name_exceptions[aff], i_g, a_g, l_g)
            if new_gid != 'NULL':
                gid_list.append(new_gid)
                city_list.append(g_city[new_gid])
                country_list.append(g_country[new_gid])
            else:
                gid_list.append('')
                city_list.append('')
                country_list.append('')                
        else:
            gid_list.append('')
            city_list.append('')
            country_list.append('')
    gid_latlong_dict = utils.update_gid_dict(gid_list, city_list, country_list)
    with open(new_filename, 'wt') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['id', 'email', 'author', 'affiliation', 'publication_year'] +
                        ['Aff resolved', 'GRID'] +
                        ['City', 'Country', 'Latitude', 'Longitude'])
        for idx, gid in enumerate(gid_list):
            if gid != '':
                writer.writerow([title_list[idx], email_list[idx], author_list[idx], aff_list[idx], int(year_list[idx])] +
                                [g_i[gid], gid, city_list[idx], country_list[idx]] +
                                [str(jj) for jj in gid_latlong_dict[gid]])
            else:
                writer.writerow([title_list[idx], email_list[idx], author_list[idx], aff_list[idx], int(year_list[idx])] +
                                ['', '', '', ''] +
                                ['', ''])

    return


def victor_exceptions(filename):
    year_list = []
    title_list = []
    author_list = []
    email_list = []
    affiliation_list = []
    with open(filename, 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for ii, row in enumerate(spamreader):
            if ii > 0:
                title_list.append(row[0])
                email_list.append(row[1])
                author_list.append(row[2])
                affiliation_list.append(row[3])
                year_list.append(row[4])
    new_aff_list = [x for _, x in sorted(zip(affiliation_list, affiliation_list),
                                         key=lambda pair: pair[0])]
    title_list = [x for _, x in sorted(zip(affiliation_list, title_list),
                                       key=lambda pair: pair[0])]
    author_list = [x for _, x in sorted(zip(affiliation_list, author_list),
                                        key=lambda pair: pair[0])]
    year_list = [x for _, x in sorted(zip(affiliation_list, year_list),
                                      key=lambda pair: pair[0])]
    email_list = [x for _, x in sorted(zip(affiliation_list, email_list),
                                      key=lambda pair: pair[0])]
    output = (year_list, title_list, author_list, new_aff_list, email_list)
    return output


def simple_mistakes(name):
    name = name.lower()
    if name.find('university') > -1:
        name = name.replace('university', ' university ')
    name = ' '.join(name.strip().split())
    return name


def resolve_names_in_file(filename='authorsUnresolvedAff.csv', exceptions_filename='exceptions_alias.csv'):
    already_parsed = {}
    if os.path.isfile(exceptions_filename):
        with open('exceptions_alias.csv', 'rt') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=':')
            for row in spamreader:
                old, new = row
                already_parsed[old] = new
    i_g_dict, g_i_dict, g_city_dict, g_country_dict, alias_g_dict, labels_g_dict = utils.consolidated_names()
    all_insti = list(i_g_dict.keys())
    alias_names = list(alias_g_dict.keys())
    labels_names = list(labels_g_dict.keys())
    all_names = all_insti + alias_names + labels_names
    completer = MyCompleter(all_names)
    readline.set_completer_delims('')
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')

    VICTOR = False
    if VICTOR:
        start_pt = 0
        end_pt = 1000
    else:
        start_pt = 1000
        end_pt = 2167

    year_list, title_list, author_list, n_aff_list, email_list = victor_exceptions(filename)
    with open('exceptions_alias.csv', 'at') as csvfile:
        writer = csv.writer(csvfile, delimiter=':')
        new_aff_list = n_aff_list[start_pt:end_pt]
        for id_prev, noidea in enumerate(new_aff_list):
            idx = id_prev + start_pt
            if noidea not in already_parsed.keys():
                testname = simple_mistakes(noidea)
                if testname in all_names:
                    if testname in all_insti:
                        uinput = testname
                    else:
                        try:
                            uinput = g_i_dict[alias_g_dict[testname]]
                        except KeyError:
                            uinput = g_i_dict[labels_g_dict[testname]]
                else:
                    a_noidea = author_list[idx] + '| \n'
                    y_noidea = year_list[idx] + '| '
                    t_noidea = title_list[idx] + '| '
                    bing.search(noidea + ' ' + author_list[idx], 3)
                    print(idx)
                    uinput = input(y_noidea + t_noidea + a_noidea + noidea + ' | Correction :  ', )
                if uinput != '':
                    already_parsed[noidea] = uinput.lower()
                    writer.writerow([noidea, uinput.lower()])
                    # print("completed percent : ", (100. * float(idx)) / float(len(new_aff_list)))

# print simple_mistakes('universityof manchester')
# print simple_mistakes('oxford university')

# victor_newfile()


# auth_aff, aff_idx, coauth_names, title_list, title_ids = utils.fetch_cosyne_affliations()  # list of list
# un_resolved_list = []
# auth_aff_dict = {}
# for ii, sub_list in enumerate(auth_aff):
#     for aff in sub_list:   # ' '.join(mystring.split())
#         new = aff.strip()
#         auth_aff_dict[len(un_resolved_list)] = ii
#         un_resolved_list.append(' '.join(new.split()))


# affiliation_list = []
# authors_list = []
# auth_count = 0
# for idx in range(len(title_list)):
#     for kk, author in enumerate(coauth_names[idx]):
#         affiliations = [int(pp)-1 for pp in aff_idx[auth_count]]
#         for affliation in affiliations:
#             authors_list.append(author)
#             affiliation_list.append(auth_aff[idx][affliation])
#         auth_count += 1
        

# , city_list, country_list, not_found, not_found_idx, candidates = utils.fetch_text_loc(affiliation_list)
# all_ids, all_insti, all_insti_city, all_insti_country, alias_ids, alias_names, labels_ids, labels_names = utils.consolidated_names()
        
# completer = MyCompleter(["h e llo", "hi", "how are you", "goodbye", "great"])

# input = raw_input("Input: ")
# print "You entered", input



