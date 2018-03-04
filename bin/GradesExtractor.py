#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
from isen.CASSession import CASSession


def main():
    # Setup the argument parser and parse them
    argsParser = argparse.ArgumentParser(description="""Gets grades in CSV.
    Outputs a .csv file in the current directory.""",
                                         prog="GradesExtractor.py")
    argsParser.add_argument("username", help="User for the login",
                            metavar="<user>")
    argsParser.add_argument("password", help="Password for the login",
                            metavar="<password>")
    argsParser.add_argument("output", help="""Name for the outputted file,
     without the extension""", metavar="<filename>")
    args = argsParser.parse_args()

    url = "https://aurion-lille.isen.fr/faces/Planning.xhtml"

    session = CASSession()
    session.setUsername(args.username)
    session.setPassword(args.password)

    with session as s:
        r = s.get(url)
        print("Response URL: " + r.url)
        print("Cookies: " + str(s.cookies))

        # Connect with the prepared session
        parser = BeautifulSoup(r.text.encode(encoding='UTF-8',
                                             errors='strict'), 'html.parser')
        payload = {"form": "form",
                   "form:largeurDivCenter": "1142",
                   "form:headerSubview:j_idt23": "form:headerSubview:j_idt23"}

        payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]
        print("Payload: " + str(payload))
        r = s.post(r.url, params=payload)

        # Now that we're logged in, we'll load the grades page
        parser = BeautifulSoup(r.text.encode(encoding='UTF-8',
                                             errors='strict'), 'html.parser')

        # The website use Richfaces forms for navigation,
        # We first need to find the j_idt code for the button we want to press
        for DOMInput in parser.find_all("a", "link"):
            if "Mes notes" in DOMInput.get_text():
                print(DOMInput["onclick"])
                sidebarIndex = DOMInput["onclick"].index("form:Sidebar")
                button = DOMInput["onclick"][sidebarIndex:sidebarIndex + 20]

        payload = {"form": "form",
                   "form:largeurDivCenter": "1142",
                   button: button}

        payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]

        print("Payload: " + str(payload))
        r = s.post("https://aurion-lille.isen.fr/faces/MainMenuPage.xhtml",
                   params=payload)

        # By now, we should have the grades in a table
        parser = BeautifulSoup(r.text.encode(encoding='UTF-8',
                                             errors='strict'), 'html.parser')

        gradesTable = parser.find("tbody", "rf-dt-b")
        grades = []
        for gradesRow in gradesTable.children:
            grade = {}
            grade["date"] = gradesRow.contents[0].get_text()
            grade["id"] = gradesRow.contents[1].get_text()
            grade["label"] = gradesRow.contents[2].get_text()
            grade["grade"] = gradesRow.contents[3].get_text()
            print(grade)
            grades.append(grade)

        # Write to the output file
        with open(args.output + ".csv", "w") as csvFile:
            for grade in grades:
                csvFile.write("{0};{1};{2};{3}\n".format(grade["date"],
                                                         grade["id"],
                                                         grade["label"],
                                                         grade["grade"]))


if __name__ == '__main__':
    main()
