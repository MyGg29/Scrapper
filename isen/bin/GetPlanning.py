#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from isen.PlanningScrapper import PlanningScrapper
from datetime import datetime, date, timedelta
import argparse

ERROR_CODE = 1
SUCCESS_CODE = 0

TODAY = date.today()


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

    # Disable verbose if silent is set
    args.verbose = False if args.silent else args.verbose

    planning = PlanningScrapper(
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

    if not planning.startSession():
        print("ERROR: Couldn't set session")
        return ERROR_CODE
    if not planning.retrieveData():
        print("ERROR: Couldn't retrieve data")
    planning.saveFiles()
    planning.stopSession()


if __name__ == '__main__':
    main()
