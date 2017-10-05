#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib.request
from bs4 import BeautifulSoup
import json
from icalendar import Calendar, Event

req = urllib.request.Request(url = "https://aurion-lille.isen.fr/faces/Planning.xhtml", method = "GET")
req.add_header("Cookie","JSESSIONID=2DBAF2CA7C879C95BBAAD74F817C1E84")

#print(req)

f = urllib.request.urlopen(req)

page = f.read().decode('utf-8')

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
ical["dtstart"] =


ical.to_ical()
file = open("calendrier.ical","w")
file.write(ical)
file.close()
