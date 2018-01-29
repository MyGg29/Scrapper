#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: handle multiple locations

import requests
import re
import locale
import sys
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import argparse

MAX_DAYS = 40
GROUPS = ["CIR1", "CIR2", "CIR3", "AP3", "AP4", "AP5", "CPG1", "CPG2", "CSI3",
          "CSIU3", "M1", "M2"]
ERROR_CODE = 1
SUCCESS_CODE = 0

TODAY = date.today()


def checkForError(response):
    if response.url.split("?")[0] == "https://cas.isen.fr/login":
        print("Login requested... You may wait for a few seconds")
        return True
    else:
        return False


def prettyPrintDict(dictionary):
    firstColumnSize = keysMaxLength(dictionary.keys())
    firstColumnFormat = "{:{c}<" + str(firstColumnSize) + "}"
    secondColumnSize = keysMaxLength(dictionary.values())
    secondColumnFormat = "{:{c}<" + str(secondColumnSize) + "}"
    print("+-" + firstColumnFormat.format("", c="-") + "-+-" +
          secondColumnFormat.format("", c="-") + "-+")
    print("| " + firstColumnFormat.format("Key", c=" ") + " | " +
          secondColumnFormat.format("Value", c=" ") + " |")
    print("+-" + firstColumnFormat.format("", c="-") + "-+-" +
          secondColumnFormat.format("", c="-") + "-+")
    for key, item in dictionary.items():
        print("| " + firstColumnFormat.format(key, c=" ") + " | " +
              secondColumnFormat.format(item, c=" ") + " |")
    print("+-" + firstColumnFormat.format("", c="-") + "-+-" +
          secondColumnFormat.format("", c="-") + "-+")


def keysMaxLength(keys):
    max = 0
    for key in keys:
        if len(key) > max:
            max = len(key)
    return max


def main():
    # Setup the argument parser and parse them
    argsParser = argparse.ArgumentParser(description="Scraps ISEN's planning \
      website. Outputs an .ics file in the current directory.", prog="python3 \
      PlanningScrapper.py")
    argsParser.add_argument("-g", help="Set the group", required=True,
                            metavar="<group>", dest="studentGroup")
    argsParser.add_argument("-s", help="Start day", metavar="<start date>",
                            default=datetime.strftime(TODAY, "%d/%m/%Y"),
                            dest="startDate")
    argsParser.add_argument("-e", help="End day", metavar="<end date>",
                            default=datetime.strftime(TODAY + timedelta(6),
                                                      "%d/%m/%Y"),
                            dest="endDate")
    argsParser.add_argument("-o", help="Name for the outputted file, without \
    the extension", metavar="<filename>", required=True, dest="outputFile")
    argsParser.add_argument("-v", help="Verbose mode", dest="verbose",
                            action="store_true")
    argsParser.add_argument("-m", help="Save the events in multiple files",
                            action="store_true", dest="multiple")
    argsParser.add_argument("-S", help="Silent - disables all messages. \
    Overwrites the -v (verbose) argument.", action="store_true", dest="silent")
    args = argsParser.parse_args()

    # Check if the group exists
    if args.studentGroup not in GROUPS:
        print("No group like " + args.studentGroup)
        return ERROR_CODE

    # Disable verbose if silent is set
    args.verbose = False if args.silent else args.verbose

    nbDays = datetime.strptime(args.endDate, "%d/%m/%Y") - \
        datetime.strptime(args.startDate, "%d/%m/%Y")

    # Display the dates
    if not args.silent:
        print("Start date: " + args.startDate)
        print("End date: " + args.endDate)
        print("We'll try to fetch " + str(nbDays) + " days")

    if nbDays > MAX_DAYS:
        print("Can't fetch more than " + str(MAX_DAYS) + " days")
        return ERROR_CODE

    url = "https://aurion-lille.isen.fr/faces/Planning.xhtml"
    eventsData = []
    eventsTeacher = []
    eventsLocation = []
    eventsSubject = []

    # Set the locale depending on the system
    # (Windows is using a different locale string)
    # We set it in French because the months and weekdays are in French
    if sys.platform in ['win32']:
        locale.setlocale(locale.LC_ALL, 'fra')
        if args.verbose:
            print("Locale set on French for Windows platform")
    else:
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        if args.verbose:
            print("Locale set on French for Unix platform")

    # Open a session and start retrieving data
    with requests.Session() as s:
        r = s.get(url)
        if checkForError(r):
            return ERROR_CODE

        if args.verbose:
            print("Response URL: " + r.url)
            print("Cookies: " + str(s.cookies))

        # This code is ugly because PEP8 require it to
        parser = BeautifulSoup(
            r.text.encode(encoding='UTF-8', errors='strict'),
            'html.parser'
        )
        payload = {"form": "form",
                   "form:largeurDivCenter": "1142"}

        # The website use Richfaces forms for navigation,
        # We first need to find the j_idt code for the button we want to press
        for DOM in parser.find_all("span", "rf-ddm-itm-lbl"):
            if args.studentGroup in DOM.get_text():
                payload[DOM.parent["id"]] = DOM.parent["id"]
        # Then we need something called "javax.faces.ViewState", whatever it is
        payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]

        if args.verbose:
            print("Payload: ")
            prettyPrintDict(payload)

        r = s.post(url, params=payload)
        if checkForError(r):
            return ERROR_CODE
        # By now, we should have received
        # https://aurion-lille.isen.fr/faces/ChoixPlanning.xhtml

        if args.verbose:
            print("Response URL: " + r.url)
            print("Cookies: " + str(s.cookies))

        parser = BeautifulSoup(
            r.text.encode(encoding='UTF-8', errors='strict'),
            'html.parser'
        )
        payload = {"form": "form",
                   "form:largeurDivCenter": "1154",
                   "form:j_idt173-value": "false",
                   "form:calendarDebutInputDate": args.startDate,
                   "form:calendarDebutInputCurrentDate":
                   "/".join(args.startDate.split("/")[1:]),
                   "form:calendarFinInputDate": args.endDate,
                   "form:calendarFinInputCurrentDate":
                   "/".join(args.endDate.split("/")[1:]),
                   "form:dataTableFavori:j_idt263": "on",
                   "javax.faces.source": "form:j_idt223",
                   "javax.faces.partial.event": "click",
                   "javax.faces.partial.execute": "form:j_idt223 @component",
                   "javax.faces.partial.render": "@component",
                   "org.richfaces.ajax.component": "form:j_idt223",
                   "form:j_idt223": "form:j_idt223",
                   "rfExt": "null",
                   "AJAX:EVENTS_COUNT": "1",
                   "javax.faces.partial.ajax": "true"}
        planningsList = parser.find_all("tbody", id="form:dataTableFavori:tb")
        for index in range(len(planningsList[0].contents)):
            payload["form:dataTableFavori:" + str(index) + ":j_idt264"] = "on"
        payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]

        if args.verbose:
            print("Payload: ")
            prettyPrintDict(payload)

        r = s.post(r.url, params=payload)
        if checkForError(r):
            return ERROR_CODE

        if args.verbose:
            print("Response URL: " + r.url)
            print("Cookies: " + str(s.cookies))

        # Now for some parsing of the page
        parser = BeautifulSoup(
            r.text.encode(encoding='UTF-8', errors='strict'), 'html.parser'
        )

        # We build the list of events by finding all labels like "Du", "Au" and
        # "Matière" and getting the next sibling label which hold the
        # information we want (starting time, ending time and subject)
        for DOM in parser.find_all("span", "ev_libelle"):
            # The sibling of "Du" holds the starting time
            if DOM.get_text() == "Du":
                container = DOM.parent.parent.parent
                classDate = container.contents[3].get_text()
                classStartHour = container.contents[7].get_text()
            # The sibling of "Au" holds the ending time
            if DOM.get_text() == "Au":
                classEndHour = DOM.parent.parent.parent.contents[7].get_text()

            # The sibling of "Matière" holds the class's subject
            if DOM.get_text() == "Matière":
                classTitle = DOM.parent.parent.parent.contents[3].get_text()

            if DOM.get_text() == "Type d'enseignement":
                classType = DOM.parent.parent.parent.contents[3].get_text()
                if classType == "Travaux Dirigés":
                    classType = "TD"
                elif classType == "Travaux Pratiques":
                    classType = "TP"
                eventsData.append({"startingTime":
                                   datetime.strptime(classDate + " " +
                                                     classStartHour,
                                                     "%A %d %B %Y %H:%M"
                                                     ),
                                   "stoppingTime":
                                   datetime.strptime(classDate + " " +
                                                     classEndHour,
                                                     "%A %d %B %Y %H:%M"
                                                     ),
                                   "title": ', '.join([classType, classTitle]),
                                   "type": classType})

        # We build the list of teachers. If nothing goes wrong, it should be
        # built in the same order than the events, thus having each element in
        # the events list correspond to an element in the teachers list with
        # the same index
        for DOM in parser.find_all("tbody", id=re.compile(".*j_idt213:tb")):
            teachersList = []
            for content in DOM.contents:
                # If it's empty, we set the teacher to None
                if content.contents[0].get_text() == "":
                    teachersList = None
                else:
                    teachersList.append(content.contents[1].get_text() + " " +
                                        content.contents[0].get_text())
            eventsTeacher.append({"teachers": teachersList})

        # We build the list of subjects. If nothing goes wrong, it should be
        # built in the same order than the events, thus having each element in
        # the events list correspond to an element in the subjects list with
        # the same index
        for DOM in parser.find_all("tbody", id=re.compile(".*j_idt252:tb")):
            if ((len(DOM.contents) == 0 or
                 DOM.contents[0].contents[0].get_text() == "")):
                eventsSubject.append({"subjects": None})
            else:
                eventsSubject.append({"subjects":
                                      DOM.contents[0].contents[0].get_text()})

        # We build the list of locations. If nothing goes wrong, it should be
        # built in the same order than the events, thus having each element in
        # the events list correspond to an element in the locations list with
        # the same index
        for DOM in parser.find_all("tbody", id=re.compile(".*j_idt205:tb")):
            if ((len(DOM.contents) == 0 or
                 DOM.contents[0].contents[0].get_text() == "")):
                eventsLocation.append({"location": None})
            else:
                eventsLocation.append({"location":
                                       DOM.contents[0].contents[0].get_text()})

        if args.verbose:
            print("We have :")
            print("- " + str(len(eventsData)) + " events")
            print("- " + str(len(eventsTeacher)) + " teachers")
            print("- " + str(len(eventsLocation)) + " locations")
            if ((len(eventsData) == len(eventsTeacher) and
                 len(eventsTeacher) == len(eventsLocation))):
                print("All clear!")

        if ((len(eventsData) != len(eventsTeacher) or
             len(eventsTeacher) != len(eventsLocation))):
            print("We have incomplete data. Skipping.")

        if not args.multiple:
            # Start creating the icalendar-compatible file
            icalString = "BEGIN:VCALENDAR\r\n"

        # Create all the events in the VEVENT format
        for i in range(0, len(eventsData)):
            if args.multiple:
                icalString = "BEGIN:VCALENDAR\r\n"

            icalString += "BEGIN:VEVENT\r\n"
            icalString += ("DTSTART:" +
                           datetime.strftime(eventsData[i]["startingTime"],
                                             "%Y%m%dT%H%M%S") + "\r\n")
            icalString += ("DTEND:" +
                           datetime.strftime(eventsData[i]["stoppingTime"],
                                             "%Y%m%dT%H%M%S") + "\r\n")
            if eventsSubject[i]["subjects"] is not None:
                icalString += ("SUMMARY:" +
                               eventsSubject[i]["subjects"] +
                               "\r\n")
            else:
                icalString += ("SUMMARY:" +
                               eventsData[i]["title"] +
                               "\r\n")
            icalString += "CATEGORIES:" + eventsData[i]["type"] + "\r\n"
            if eventsTeacher[i]["teachers"] is not None:
                for teacher in eventsTeacher[i]["teachers"]:
                    icalString += "ATTENDEE:" + teacher + "\r\n"
                icalString += ("DESCRIPTION:" + eventsData[i]["type"] + " - " +
                               '/'.join(eventsTeacher[i]["teachers"]) + "\r\n")
            if eventsLocation[i]["location"] is not None:
                icalString += ("LOCATION:" +
                               eventsLocation[i]["location"] + "\r\n")
            icalString += "END:VEVENT\r\n"

            if args.multiple:
                icalString += "END:VCALENDAR\r\n"

                # Write to the output files
                filename = args.outputFile + str(i).zfill(3) + ".ics"
                with open(filename, "w") as f:
                    f.write(icalString)

        if not args.multiple:
            icalString += "END:VCALENDAR\r\n"

            # Write to the output file
            with open(args.outputFile + ".ics", "w") as f:
                f.write(icalString)

    return SUCCESS_CODE


if __name__ == '__main__':
    main()
