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

auth_aff, aff_idx, coauth_names, title_list, title_ids = utils.fetch_cosyne_affliations()  # list of list
# un_resolved_list = []
# auth_aff_dict = {}
# for ii, sub_list in enumerate(auth_aff):
#     for aff in sub_list:   # ' '.join(mystring.split())
#         new = aff.strip()
#         auth_aff_dict[len(un_resolved_list)] = ii
#         un_resolved_list.append(' '.join(new.split()))


affiliation_list = []
authors_list = []
auth_count = 0
for idx in range(len(title_list)):
    for kk, author in enumerate(coauth_names[idx]):
        affiliations = [int(pp)-1 for pp in aff_idx[auth_count]]
        for affliation in affiliations:
            authors_list.append(author)
            affiliation_list.append(auth_aff[idx][affliation])
        auth_count += 1
        
insti_list, city_list, country_list, not_found, not_found_idx, candidates = utils.fetch_text_loc(affiliation_list)
all_ids, all_insti, all_insti_city, all_insti_country, alias_ids, alias_names, labels_ids, labels_names = utils.consolidated_names()
        
# completer = MyCompleter(["h e llo", "hi", "how are you", "goodbye", "great"])

completer = MyCompleter(all_insti + alias_names + labels_names)
readline.set_completer_delims('')
readline.set_completer(completer.complete)
readline.parse_and_bind('tab: complete')
# input = raw_input("Input: ")
# print "You entered", input

already_parsed = {}
if os.path.isfile('exceptions_alias.csv'):
    with open('exceptions_alias.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=':')
        for row in spamreader:
            old, new = row
            already_parsed[old] = new

with open('exceptions_alias.csv', 'ab') as csvfile:
    writer = csv.writer(csvfile, delimiter=':')
    for ii, noidea in enumerate(not_found):
        if noidea not in already_parsed.keys():
            author_noidea = authors_list[not_found_idx[ii]]
            auth_noidea = author_noidea + '| \n'
            bing.search(noidea + ' ' + auth_noidea, 3)
            input = raw_input(auth_noidea + noidea + ' | Correct :  ', )
            if input != '':
                already_parsed[noidea] = input.lower()
                writer.writerow([noidea, input.lower()])
                print "completed percent : ", (100. * float(ii)) / float(len(not_found))
