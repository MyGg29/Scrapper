import requests, re, locale, sys
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import argparse

## Setup the argument parser and parse them
argsParser = argparse.ArgumentParser(description = "Scraps ISEN's planning website. Outputs an .ics file in the current directory.", prog = "python3 PlanningScrapper.py")
argsParser.add_argument("-g", help = "Set the group", required = True, metavar = "<group>", dest = "studentGroup")
argsParser.add_argument("-s", help = "Start day", metavar = "<start date>", default = datetime.strftime(date.today(), "%d/%m/%Y"), dest = "startDate")
argsParser.add_argument("-e", help = "End day", metavar = "<end date>", default = datetime.strftime(date.today() + timedelta(days=6), "%d/%m/%Y"), dest = "endDate")
argsParser.add_argument("-o", help = "Name for the outputted file, without the extension", metavar = "<filename>", required = True, dest = "outputFile")
args = argsParser.parse_args()

## Display the dates
print("Start date: " + args.startDate)
print("End date: " + args.endDate)

url = "https://aurion-lille.isen.fr/faces/Planning.xhtml"
eventsData = []
eventsTeacher = []
eventsLocation = []

icalString = ""

## Set the locale depending on the system
## (Windows is using a different locale string)
## We set it in French because the months and weekdays are in French
if sys.platform in ['win32']:
	locale.setlocale(locale.LC_ALL, 'fra')
	print("Locale set for Windows platform")
else:
	locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
	print("Locale set for Unix platform")

## Open a session and start retrieving data
with requests.Session() as s:
	r = s.get(url)
	print("Response URL: " + r.url)
	print("Cookies: " + str(s.cookies))

	parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
	payload = {"form": "form",
			   "form:largeurDivCenter": "1142"}

	## The website use Richfaces forms for navigation,
	## We first need to find the j_idt code for the button we want to press
	for DOMInput in parser.find_all("span", "rf-ddm-itm-lbl"):
		if args.studentGroup in DOMInput.get_text():
			payload[DOMInput.parent["id"]] = DOMInput.parent["id"]
	## Then we need something called "javax.faces.ViewState", whatever it is
	payload["javax.faces.ViewState"] = parser.select_one("#j_id1:javax.faces.ViewState:0")["value"]
	print("Payload: " + str(payload))
	r = s.post(url, params = payload)
	## By now, we should have received https://aurion-lille.isen.fr/faces/ChoixPlanning.xhtml
	print("Response URL: " + r.url)
	parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
	print("Cookies: " + str(s.cookies))
	payload = {"form": "form",
			   "form:largeurDivCenter": "1154",
			   "form:j_idt263-value": "false",
			   "form:calendarDebutInputDate": args.startDate,
			   "form:calendarDebutInputCurrentDate": "/".join(args.startDate.split("/")[1:]),
			   "form:calendarFinInputDate": args.endDate,
			   "form:calendarFinInputCurrentDate": "/".join(args.endDate.split("/")[1:]),
			   "form:dataTableFavori:j_idt150": "on",
			   "form:dataTableFavori:0:j_idt151": "on",
			   "javax.faces.source": "form:j_idt110",
			   "javax.faces.partial.event": "click",
			   "javax.faces.partial.execute": "form:j_idt110 @component",
			   "javax.faces.partial.render": "@component",
			   "org.richfaces.ajax.component": "form:j_idt110",
			   "form:j_idt110": "form:j_idt110",
			   "rfExt": "null",
			   "AJAX:EVENTS_COUNT": "1",
			   "javax.faces.partial.ajax": "true"}
	payload["javax.faces.ViewState"] = parser.select_one("#j_id1:javax.faces.ViewState:0")["value"]
	print("Payload: " + str(payload))
	r = s.post(r.url, params = payload)

	## Now for some parsing of the page
	parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')

	## We build the list of events by finding all labels like "Du", "Au" and
	## "Matière" and getting the next sibling label which hold the information
	## we want (starting time, ending time and subject)
	for DOMInput in parser.find_all("span", "ev_libelle"):
		## The sibling of "Du" holds the starting time
		if DOMInput.get_text() == "Du":
			classDate = DOMInput.parent.parent.parent.contents[3].get_text()
			classStartHour = DOMInput.parent.parent.parent.contents[7].get_text()
		## The sibling of "Au" holds the ending time
		if DOMInput.get_text() == "Au":
			classEndHour = DOMInput.parent.parent.parent.contents[7].get_text()
		## The sibling of "Matière" holds the class's subject
		if DOMInput.get_text() == "Matière":
			eventsData.append({"startingTime": datetime.strptime(classDate + " " + classStartHour, "%A %d %B %Y %H:%M"),
							   "stoppingTime": datetime.strptime(classDate + " " + classEndHour, "%A %d %B %Y %H:%M"),
							   "title": DOMInput.parent.parent.parent.contents[3].get_text()})

	## We build the list of teachers. If nothing goes wrong, it should be
	## built in the same order than the events, thus having each element in the
	## events list correspond to an element in the teachers list with the same
	## index
	for DOMInput in parser.find_all("tr", id = re.compile(".*j_idt212:0")):
		eventsTeacher.append({"teacher": DOMInput.contents[1].get_text() + " " + DOMInput.contents[0].get_text()})

	## We build the list of locations. If nothing goes wrong, it should be
	## built in the same order than the events, thus having each element in the
	## events list correspond to an element in the locations list with the same
	## index
	for DOMInput in parser.find_all("td", id = re.compile(".*0:j_idt205")):
		eventsLocation.append({"location": DOMInput.get_text()})

	## Start creating the icalendar-compatible file
	icalString += "BEGIN:VCALENDAR\r\n"

	## Create all the events in the VEVENT format
	for i in range(0, len(eventsData)):
		icalString += "BEGIN:VEVENT\r\n"
		icalString += "UID:" + str(i) + "\r\n"
		icalString += "DTSTART:" + datetime.strftime(eventsData[i]["startingTime"], "%Y%m%dT%H%M%S") + "\r\n"
		icalString += "DTEND:" + datetime.strftime(eventsData[i]["stoppingTime"], "%Y%m%dT%H%M%S") + "\r\n"
		icalString += "SUMMARY:" + eventsData[i]["title"] + "\r\n"
		icalString += "ORGANIZER:" + eventsTeacher[i]["teacher"] + "\r\n"
		icalString += "DESCRIPTION:" + eventsTeacher[i]["teacher"] + "\r\n"
		icalString += "LOCATION:" + eventsLocation[i]["location"] + "\r\n"
		icalString += "END:VEVENT\r\n"

	icalString += "END:VCALENDAR\r\n"

	## Write to the output file
	with open(args.outputFile + ".ics", "w") as f:
		f.write(icalString)
