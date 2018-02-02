#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
from isen.CASSession import CASSession


def main():
    # Setup the argument parser and parse them
    argsParser = argparse.ArgumentParser(description="""Gets ISEN's classrooms
     availability in CSV. Outputs a .csv file in the current directory.""",
                                         prog="RoomsExtractor.py")
    argsParser.add_argument("-u", help="Username", required=True,
                            metavar="<username>", dest="username")
    argsParser.add_argument("-p", help="Password", required=True,
                            metavar="<password>", dest="password")
    argsParser.add_argument("-o", help="""Name for the outputted file, without the
     extension""", metavar="<filename>", required=True, dest="outputFile")
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

        # Now that we're logged in, we'll load the room page
        parser = BeautifulSoup(r.text.encode(encoding='UTF-8',
                                             errors='strict'), 'html.parser')

        # The website use Richfaces forms for navigation,
        # We first need to find the j_idt code for the button we want to press
        for DOMInput in parser.find_all("a", "link"):
            if "Salles disponibles" in DOMInput.get_text():
                print(DOMInput["onclick"])
                sidebarIndex = DOMInput["onclick"].index("form:Sidebar")
                button = DOMInput["onclick"][sidebarIndex:sidebarIndex + 21]

        payload = {"form": "form",
                   "form:largeurDivCenter": "1142",
                   button: button}

        payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0"
        )["value"]

        print("Payload: " + str(payload))
        r = s.post("https://aurion-lille.isen.fr/faces/MainMenuPage.xhtml",
                   params=payload)

        # By now, we should have the room page
        # and the link for exporting in CSV
        parser = BeautifulSoup(r.text.encode(encoding='UTF-8',
                                             errors='strict'), 'html.parser')

        payload = {"form": "form",
                   "form:largeurDivCenter": "1142",
                   "form:j_idt171-value": "false",
                   "form:menuItem1": "form:menuItem1"}

        payload["javax.faces.ViewState"] = parser.select_one(
            "#j_id1:javax.faces.ViewState:0")["value"]
        print("Payload: " + str(payload))
        r = s.post("https://aurion-lille.isen.fr/faces/ChoixDonnee.xhtml",
                   params=payload)

        # Write to the output file
        with open(args.outputFile + ".csv", "w") as csvFile:
            csvFile.write(r.text)


if __name__ == '__main__':
    main()
