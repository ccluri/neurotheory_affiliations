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


def victor_exceptions(filename):
    year_list = []
    title_list = []
    author_list = []
    affiliation_list = []
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for ii, row in enumerate(spamreader):
            if ii > 0:
                title_list.append(row[0])
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
    output = (year_list, title_list, author_list, new_aff_list)
    return output


def simple_mistakes(name):
    if name.find('university') > -1:
        name = name.replace('university', ' university ')
    name = ' '.join(name.strip().split())
    return name


already_parsed = {}
if os.path.isfile('exceptions_alias.csv'):
    with open('exceptions_alias.csv', 'rb') as csvfile:
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
    
filename = os.path.join('authorsUnresolvedAff.csv')
year_list, title_list, author_list, new_aff_list = victor_exceptions(filename)
with open('exceptions_alias.csv', 'ab') as csvfile:
    writer = csv.writer(csvfile, delimiter=':')
    for idx, noidea in enumerate(new_aff_list):
        if noidea not in already_parsed.keys():
            testname = simple_mistakes(noidea)
            if testname in all_names:
                if testname in all_insti:
                    uinput = testname
                else:
                    try:
                        uinput = g_i_dict[alias_g_dict(testname)]
                    except KeyError:
                        uinput = g_i_dict[labels_g_dict(testname)]
            else:
                a_noidea = author_list[idx] + '| \n'
                y_noidea = year_list[idx] + '| '
                t_noidea = title_list[idx] + '| '
                bing.search(noidea + ' ' + author_list[idx], 3)
                uinput = raw_input(y_noidea + t_noidea + a_noidea + noidea + ' | Correction :  ', )
            if uinput != '':
                already_parsed[noidea] = uinput.lower()
                writer.writerow([noidea, uinput.lower()])
                print("completed percent : ", (100. * float(idx)) / float(len(new_aff_list)))

# print simple_mistakes('universityof manchester')
# print simple_mistakes('oxford university')














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



