import readline
import affiliation_utils as utils
import csv
import os

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

auth_aff, aff_idx, coauth_names = utils.fetch_cosyne_affliations()  # list of list
un_resolved_list = []
auth_aff_dict = {}
for ii, sub_list in enumerate(auth_aff):
    for aff in sub_list:   # ' '.join(mystring.split())
        new = aff.strip()
        auth_aff_dict[len(un_resolved_list)] = ii
        un_resolved_list.append(' '.join(new.split()))
        
        
insti_list, city_list, country_list, not_found, not_found_idx, candidates = utils.fetch_text_loc(un_resolved_list)
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
            coauths = coauth_names[auth_aff_dict[not_found_idx[ii]]]
            coauths = ','.join(coauths)
            coauths = coauths + '| \n'
            input = raw_input(coauths + noidea + ' | Correct :  ', )
            print "You entered", input
            already_parsed[noidea] = input.lower()
            writer.writerow([noidea, input.lower()])
            print "completed percent : ", (100. * float(ii)) / float(len(not_found))
