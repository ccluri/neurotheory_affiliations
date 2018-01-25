#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
import urllib, urllib2


def search(query, number=3):
    address = "http://www.bing.com/search?q=%s" % (urllib.quote_plus(query))

    getRequest = urllib2.Request(address, None, {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})

    urlfile = urllib2.urlopen(getRequest)
    htmlResult = urlfile.read(200000)
    urlfile.close()

    soup = BeautifulSoup(htmlResult)

    [s.extract() for s in soup('span')]
    unwantedTags = ['a', 'strong', 'cite']
    for tag in unwantedTags:
        for match in soup.findAll(tag):
            match.replaceWithChildren()

    results = soup.findAll('li', { "class" : "b_algo" })
    for result in results[:number]:
        print "# TITLE: " + str(result.find('h2')).replace(" ", " ") + "\n#"
        print "# DESCRIPTION: " + str(result.find('p')).replace(" ", " ")
        print "# ___________________________________________________________\n#"
    return results

if __name__=='__main__':
    links = search('Shakespeare', 5)
