#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib.request
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime

try:
	raw = open("rawpage.txt", "r")
	page = raw.read()
except ValueError:	
	req = urllib.request.Request(url = "https://aurion-lille.isen.fr/faces/Planning.xhtml", method = "GET")
	req.add_header("Cookie","JSESSIONID=8D848A1227953213400DFADFB0D2D821")
	f = urllib.request.urlopen(req)
	page = f.read().decode('utf-8')

#pagefile = open("rawpage.txt", "w")
#pagefile.write(page)

soup = BeautifulSoup(page, 'html.parser')

soup.prettify()

evenement = soup.find_all("div", {"class" : "evenement"})
for f in evenement:
    print(f.string)

detail = []
for i in range(0, len(evenement)):
    detail.append(soup.find(id = "form:composantsInterventions:%d:detail" % i))
    print(i)

dDebut =  []
hDebut = []
dFin = []
hFin = []
for f in detail:
    dDebut.append(f.div.next_sibling.tbody.tr.td.find_next("td").text)
    hDebut.append(f.div.next_sibling.tbody.tr.td.find_next("td").find_next("td").find_next("td").text)
    dFin.append(f.div.next_sibling.tbody.tr.find_next_sibling("tr").td.find_next("td").text)
    hFin.append(f.div.next_sibling.tbody.tr.find_next_sibling("tr").td.find_next("td").find_next("td").find_next("td").text)

print(dDebut)
print(hDebut)
print(dFin)
print(hFin)

ical = Calendar()
association = {'janvier' : 1, 'fevrier' : 2, 'mars' : 3, 'avril' : 4, 'mai' : 5, 'juin' : 6, 'juillet' : 7, 'aout' : 8, 'septembre' : 9, 'octobre' : 10, 'novembre' : 11, 'decembre' : 12}

print(dDebut[i].split(" ")[3])
'''
for i in range(0, len(evenement)):
	ical.add("dtstart", datetime.datetime(
											dDebut[i].split(" ")[3], 
											association[dDebut[i].split(" ")[2], 
											dDebut[i].split(" ")[1], 
											hDebut[i].split(":")[0], 
											hDebut[i].split(":")[1]
										)
			)
    print(datetime.datetime(dDebut[i].split(" ")[3], association[dDebut[i].split(" ")[2], dDebut[i].split(" ")[1], hDebut[i].split(":")[0], hDebut[i].split(":")[1]))
	1+1
#ical.to_ical()
#file = open("calendrier.ical","w")
#file.write(ical)
#file.close()
'''