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
from CASSession import CASSession

MAX_DAYS = 40
GROUPS = ["CIR1", "CIR2", "CIR3", "AP3", "AP4", "AP5", "CPG1", "CPG2", "CSI3",
          "CSIU3", "M1", "M2"]
ERROR_CODE = 1
SUCCESS_CODE = 0

TODAY = date.today()

URL = "https://aurion-lille.isen.fr/faces/Planning.xhtml"


class PlanningScrapper(object):

    """docstring for PlanningScrapper."""
    def __init__(self, group, startDate, endDate, output, user=None,
                 password=None, multiple=False, verbose=False, silent=False,
                 login=False):
        super(PlanningScrapper, self).__init__()
        self.group = group
        self.startDate = startDate
        self.endDate = endDate
        self.multiple = multiple
        self.user = user
        self.password = password
        self.output = output
        self.verbose = verbose
        self.silent = silent
        self.login = login

        self.session = None
        self.payload = None

        # Set the locale depending on the system
        # (Windows is using a different locale string)
        # We set it in French because the months and weekdays are in French
        if sys.platform in ['win32']:
            locale.setlocale(locale.LC_ALL, 'fra')
            if self.verbose:
                print("Locale set on French for Windows platform")
        else:
            locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
            if self.verbose:
                print("Locale set on French for Unix platform")

        self.startSession()
        page = self.loadHomePage()
        if page == ERROR_CODE:
            print("ERROR")
            return ERROR_CODE
        if login:
            page = self.loadPrivatePlanning(page)
        else:
            page = self.loadPublicPlanning(page)
        self.session.close()

        if page == ERROR_CODE:
            print("ERROR")
            return ERROR_CODE

        parser = BeautifulSoup(
            page.text.encode(encoding='UTF-8', errors='strict'), 'html.parser'
        )

        eventsData = self.getEvents(parser)
        eventsTeacher = self.getTeachers(parser)
        eventsLocation = self.getLocations(parser)
        eventsSubject = self.getSubjects(parser)

        self.saveFiles(eventsData, eventsTeacher, eventsLocation,
                       eventsSubject, self.output)

        self.result = SUCCESS_CODE

    def checkForErrors(self, response, expectedResponse=None):
        ret = False
        if response.url.split("?")[0] == "https://cas.isen.fr/login":
            print("Login requested... You may wait for a few seconds")
            ret = True
        if expectedResponse is not None and expectedResponse != response.url:
            print("Not the page expected, please check with verbose mode")
            ret = True
        return ret

    def startSession(self):
        if self.login:
            self.session = CASSession()
            self.session.setUsername(self.user)
            self.session.setPassword(self.password)
            self.session.getSession()
        else:
            self.session = requests.Session()

    def loadHomePage(self):
        r = self.session.get(URL)
        if self.checkForErrors(r):
            return ERROR_CODE

        if self.verbose:
            print("Response URL: " + r.url)
            print("Cookies: " + str(self.session.cookies))

        self.payload = {"form": "form",
                        "form:largeurDivCenter": "1142"}

        return r

    def loadPublicPlanning(self, homePage):
        # We need to parse the page to get the j_idt (see below) for the
        # planning
        parser = BeautifulSoup(
            homePage.text.encode(encoding='UTF-8', errors='strict'),
            'html.parser'
        )

        # The website use Richfaces forms for navigation,
        # We first need to find the j_idt code for the button we want to press
        for DOM in parser.find_all("span", "rf-ddm-itm-lbl"):
            if self.group in DOM.get_text():
                self.payload[DOM.parent["id"]] = DOM.parent["id"]

        # Then we need something called "javax.faces.ViewState", whatever it is
        self.payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]

        if self.verbose:
            print("Payload: ")
            prettyPrintDict(self.payload)

        # We send a POST request with the payload we built previously to the
        # home page. This should redirect us to
        # https://aurion-lille.isen.fr/faces/ChoixPlanning.xhtml
        r = self.session.post(homePage.url, params=self.payload)
        if self.checkForErrors(r, "https://aurion-lille.isen.fr/" +
                               "faces/ChoixPlanning.xhtml"):
            return ERROR_CODE

        if self.verbose:
            print("Response URL: " + r.url)
            print("Cookies: " + str(self.session.cookies))

        # We parse the new page to get all the j_idt we need to enable
        # (one per planning) and build the payload
        parser = BeautifulSoup(
            r.text.encode(encoding='UTF-8', errors='strict'),
            'html.parser'
        )

        # Let's build a first part for common data
        self.payload = {"form": "form",
                        "form:largeurDivCenter": "1154",
                        "form:j_idt173-value": "false",
                        "form:calendarDebutInputDate": self.startDate,
                        "form:calendarDebutInputCurrentDate":
                        "/".join(self.startDate.split("/")[1:]),
                        "form:calendarFinInputDate": self.endDate,
                        "form:calendarFinInputCurrentDate":
                        "/".join(self.endDate.split("/")[1:]),
                        "form:dataTableFavori:j_idt263": "on",
                        "javax.faces.source": "form:j_idt223",
                        "javax.faces.partial.event": "click",
                        "javax.faces.partial.execute": "form:j_idt223" +
                        " @component",
                        "javax.faces.partial.render": "@component",
                        "org.richfaces.ajax.component": "form:j_idt223",
                        "form:j_idt223": "form:j_idt223",
                        "rfExt": "null",
                        "AJAX:EVENTS_COUNT": "1",
                        "javax.faces.partial.ajax": "true"}

        # Find all available plannings
        planningsList = parser.find_all("tbody", id="form:dataTableFavori:tb")
        for index in range(len(planningsList[0].contents)):
            # And add them to the payload
            self.payload["form:dataTableFavori:" + str(index) +
                         ":j_idt264"] = "on"

        # Again, we need the javax.faces.ViewState for whatever reason
        self.payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]

        if self.verbose:
            print("Payload: ")
            prettyPrintDict(self.payload)

        # We send a POST request to the current page with the payload we built
        r = self.session.post(r.url, params=self.payload)

        # Now if everything went fine, we expect to be redirected to
        # https://aurion-lille.isen.fr/faces/Planning.xhtml
        # with the data ready to be parsed (mmmh fresh data)
        if self.checkForErrors(r):
            return ERROR_CODE

        if self.verbose:
            print("Response URL: " + r.url)
            print("Cookies: " + str(self.session.cookies))

        return r

    def loadPrivatePlanning(self):
        pass

    def getEvents(self, parser):
        eventsData = []

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

            # The sibling of "Type d'enseignement" holds class type
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

        return eventsData

    def getLocations(self, parser):
        eventsLocation = []

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

        return eventsLocation

    def getTeachers(self, parser):
        eventsTeacher = []

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

        return eventsTeacher

    def getSubjects(self, parser):
        eventsSubject = []

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

        return eventsSubject

    def saveFiles(self, eventsData, eventsTeacher, eventsLocation,
                  eventsSubject, filename):
        if self.verbose:
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
            return ERROR_CODE

        if not self.multiple:
            # Start creating the icalendar-compatible file
            icalString = "BEGIN:VCALENDAR\r\n"

        # Create all the events in the VEVENT format
        for i in range(0, len(eventsData)):
            if self.multiple:
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

            if self.multiple:
                icalString += "END:VCALENDAR\r\n"

                # Write to the output files
                filename = self.output + str(i).zfill(3) + ".ics"
                with open(filename, "w") as f:
                    f.write(icalString)

        if not self.multiple:
            icalString += "END:VCALENDAR\r\n"

            # Write to the output file
            with open(self.output + ".ics", "w") as f:
                f.write(icalString)


def prettyPrintDict(dictionary):
    firstColumnSize = len(max(dictionary.keys(), key=len))
    firstColumnFormat = "{:{c}<" + str(firstColumnSize) + "}"
    secondColumnSize = len(max(dictionary.values(), key=len))
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
    argsParser.add_argument("-l", help="Login - use login to get personalized \
                            planning", action="store_true", dest="login")
    argsParser.add_argument("-u", help="User for the login", dest="user",
                            metavar="<user>")
    argsParser.add_argument("-p", help="Password for the login",
                            dest="password", metavar="<password>")
    args = argsParser.parse_args()

    # Check if the group exists
    if args.studentGroup not in GROUPS:
        print("No group like " + args.studentGroup)
        return ERROR_CODE

    # Disable verbose if silent is set
    args.verbose = False if args.silent else args.verbose

    # Checks for the login
    if args.login:
        if args.password is None or args.login is None:
            print("No user or password given for the user")
            return ERROR_CODE

    nbDays = (datetime.strptime(args.endDate, "%d/%m/%Y") -
              datetime.strptime(args.startDate, "%d/%m/%Y")).days

    # Display the dates
    if not args.silent:
        print("Start date: " + args.startDate)
        print("End date: " + args.endDate)
        print("We'll try to fetch " + str(nbDays) + " days")

    if nbDays > MAX_DAYS:
        print("Can't fetch more than " + str(MAX_DAYS) + " days")
        return ERROR_CODE

    PlanningScrapper(
        group=args.studentGroup,
        startDate=args.startDate,
        endDate=args.endDate,
        output=args.outputFile,
        user=args.user,
        password=args.password,
        multiple=args.multiple,
        verbose=args.verbose,
        silent=args.silent,
        login=args.login)


if __name__ == '__main__':
    main()
