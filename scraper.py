# This script has two goals:
# i) To record changes with the lobbyist register and record themm in a sqlite database on Morph.io.
# ii) To alert people to changes to lobbyists via:
#   a) mailgun email list (TBC)
#   b) a Twitter bot
#   c) to politics forum APH.life (TBC)

# First let's start with imports

import requests
from bs4 import BeautifulSoup
import datetime
import scraperwiki
import os
from operator import itemgetter
import tweet # This is another python script to handle Tweeting (with Tweepy)
import random
import time

print help("modules")

tabs = {"agencies":['ABN','Trading Name','Agency Name','Updated'],
       "client": ['Agency Name','Client Name'],
       "lobbyists": ['Agency Name','Lobbyist Name','Lobbyist Position','Former Government Representative','Cessation Date']}

interesting = [
"intriguing", "gripping", "diverting", "fascinating", "absorbing", "newsworthy", 
"interestingness", "riveting", "engrossing", "amusing", "interest", "entertaining", 
"exciting","wow","gee","mmmm","achtung","my oh my","would you look at that","check it yo",
"kapow","blam","ooow","notable","well","uh huh"]

# Check if table exists...

old = {}
dbtest = False
try:
    for kind in tabs.keys():
        old[kind] = scraperwiki.sql.select("* from %s where End = ''"%kind)
        print 'Yesterday the current record count for %s was:'%kind,len(old[kind])
        dbtest = True

except Exception as e:
    print 'Just as I suspected:',e

new = {}

for kind in tabs.keys():
    response = requests.get("http://lobbyists.pmc.gov.au/export/export_%s.cfm"%kind)
    response.encoding = 'Windows-1252'
    soup = BeautifulSoup(response.text,'lxml')
    data = []
    names = [el.text for el in soup.html.body.table.find_all('tr')[1].find_all('th')]
    for tr in soup.html.body.table.find_all('tr')[2:]:
        row = {}
        tds = tr.find_all('td')
        for i,td in enumerate(tds):
            tight = td.text.strip().replace("Alkar","BOOOOOO")
            row[names[i]] = tight
        row[u'Start'] = unicode(datetime.date.today().strftime("%d-%b-%Y"))
        row[u'End'] = ''
        data.append(row)
    new[kind] = data
    if dbtest == False:
        scraperwiki.sqlite.save(unique_keys=tabs[kind],data=data,table_name=kind)

if dbtest == True:
    # check for new items not in old items - start them today
    for kind in tabs.keys():
        for item in new[kind]:
            gothim = False
            for olditem in old[kind]:
                if itemgetter(*tabs[kind])(item) == itemgetter(*tabs[kind])(olditem):
                    #print itemgetter(*tabs[kind])(item),itemgetter(*tabs[kind])(olditem)
                    gothim = True
            if gothim == False:
                #print 'NEW',item
                item[u'Start'] = unicode(datetime.date.today().strftime("%d-%b-%Y"))
                item[u'End'] = ''
                scraperwiki.sqlite.save(unique_keys=tabs[kind],data=item,table_name=kind)
                if kind=='client':
                    tweet.this('%s. %s is now lobbying for %s.'%(random.choice(interesting).capitalize(),item['Agency Name'],item['Client Name']))
                    time.sleep(23)
                if kind=='lobbyists':
                    tweet.this('%s. %s is now a %s for %s.'%(random.choice(interesting).capitalize(),item['Lobbyist Name'],item['Lobbyist Position'],item['Agency Name']))
                    time.sleep(23)

    # check for old items no longer in new items - end them today
    for kind in tabs.keys():
        for olditem in old[kind]:
            gothim = False
            for newitem in new[kind]:
                if itemgetter(*tabs[kind])(newitem) == itemgetter(*tabs[kind])(olditem):
                    gothim = True
            if gothim == False:
                #print 'OLD',olditem
                olditem[u'End'] = unicode(datetime.date.today().strftime("%d-%b-%Y"))
                scraperwiki.sqlite.save(unique_keys=tabs[kind],data=olditem,table_name=kind)
                if kind=='client':
                    tweet.this('%s. %s is no longer lobbying for %s.'%(random.choice(interesting).capitalize(),olditem['Agency Name'],olditem['Client Name']))
                    time.sleep(23)
                if kind=='lobbyists':
                    tweet.this('%s. %s is no longer a %s for %s.'%(random.choice(interesting).capitalize(),olditem['Lobbyist Name'],olditem['Lobbyist Position'],item['Agency Name']))
                    time.sleep(23)
    