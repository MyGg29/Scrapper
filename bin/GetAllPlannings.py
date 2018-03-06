#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import configparser
from datetime import datetime, timedelta
from time import sleep
import os
from isen.PlanningScrapper import PlanningScrapper
import requests

MAX_DAYS = 40
GROUPS = ["AP3", "AP4", "AP5", "CIR1", "CIR2", "CIR3", "CPG1", "CPG2", "CSI3",
          "CSIU3", "M1", "M2"]

# Those are blacklisted group because we don't handle them yet, see
# PlanningScrapper.py for more information
BLACKLISTED_GROUPS = []

session = requests.Session()


def getChunk(startDate, endDate, chunkIndex, group, args,
             strikes=0, session=None):
    planning = PlanningScrapper(
        group=group,
        output=args.savePath + "/" + group + "/" + str(chunkIndex),
        startDate=datetime.strftime(startDate, "%d/%m/%Y"),
        endDate=datetime.strftime(endDate, "%d/%m/%Y"),
        user=args.user,
        password=args.password,
        multiple=args.multiple,
        verbose=args.verbose,
        silent=args.silent,
        login=args.login
    )

    if session is None:
        planning.startSession()
    else:
        planning.setSession(session)

    if not planning.sessionIsSet():
        print("\x1B[31;40m" + "FAILURE" + "\x1B[0m")
        with open(args.logPath + "/isen-plannings.log", "a") as logFile:
            logFile.write("FAILURE: " + group + " - " +
                          datetime.strftime(startDate, "%d/%m/%Y") + " -> " +
                          datetime.strftime(endDate, "%d/%m/%Y") + "\n")

        strikes += 1
        return [0, strikes]

    if not planning.retrieveData():
        print("\x1B[31;40m" + "FAILURE" + "\x1B[0m")
        with open(args.logPath + "/isen-plannings.log", "a") as logFile:
            logFile.write("FAILURE: " + group + " - " +
                          datetime.strftime(startDate, "%d/%m/%Y") + " -> " +
                          datetime.strftime(endDate, "%d/%m/%Y") + "\n")

        strikes += 1
        if strikes >= 3:
            print("3 strikes, using aggressive waiting")
            return [30, 0]
        else:
            return [5, strikes]
        return [5, 0]

    for rmFile in os.listdir(args.savePath + "/" + group):
        if rmFile[0] == chunkIndex:
            os.remove(args.savePath + "/" + group + "/" + rmFile)

    planning.saveFiles()

    if session is None:
        planning.stopSession()

    print("\x1B[32;40m" + "SUCCESS" + "\x1B[0m")
    with open(args.logPath + "/isen-plannings.log", "a") as logFile:
        logFile.write("SUCCESS: " + group + " - " +
                      datetime.strftime(startDate, "%d/%m/%Y") + " -> " +
                      datetime.strftime(endDate, "%d/%m/%Y") + "\n")

    return [0, 0]


def main():
    # Setup the argument parser and parse them
    argsParser = argparse.ArgumentParser(description="""Gets all ISEN's
     plannings and save them in a folder in ical format.""",
                                         prog="GetAllPlanning.py")
    argsParser.add_argument("-c", help="Configuration file", dest="conf",
                            metavar="<conf file>",
                            default="/etc/isen-planning.conf")
    argsParser.add_argument("-v", help="Verbose mode", dest="verbose",
                            action="store_const", const=True)
    argsParser.add_argument("-m", help="Save the events in multiple files",
                            action="store_const", dest="multiple", const=True)
    argsParser.add_argument("-S", help="Silent - disables all messages. \
    Overwrites the -v (verbose) argument.", action="store_const",
                            dest="silent", const=True)
    argsParser.add_argument("-l", help="Enable login", action="store_const",
                            dest="login", const=True)
    argsParser.add_argument("-u", help="User for the login", dest="user",
                            metavar="<user>")
    argsParser.add_argument("-p", help="Password for the login",
                            dest="password", metavar="<password>")
    argsParser.add_argument("-P", help="""The path where to save the files that
     have been retrieved""", metavar="<save path>", dest="savePath")
    argsParser.add_argument("-L", help="""The path where to save the
     log file""", metavar="<log path", dest="logPath")
    args = argsParser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.conf)
    args.multiple = (config['general'].getboolean('multipleFiles')
                     if args.multiple is None else args.multiple)
    args.verbose = (config['general'].getboolean('verbose')
                    if args.verbose is None else args.verbose)
    args.silent = (config['general'].getboolean('silent')
                   if args.silent is None else args.silent)
    args.savePath = (config['paths']['savePath']
                     if args.savePath is None else args.savePath)
    args.logPath = (config['paths']['logPath']
                    if args.logPath is None else args.logPath)
    args.login = (config['user'].getboolean('loginEnabled')
                  if args.login is None else args.login)
    args.user = config['user']['user'] if args.user is None else args.user
    args.password = (config['user']['password']
                     if args.password is None else args.password)

    startDate = datetime(year=2017, month=9, day=1)
    endDate = datetime(year=2018, month=7, day=1)

    totalDays = (endDate - startDate).days
    nbBigChunks = totalDays // MAX_DAYS
    reste = (totalDays % MAX_DAYS) - nbBigChunks

    session = requests.session()
    sleepTime = 0
    strikes = 0

    print("We need to get " + str(totalDays) + " days in " +
          str(nbBigChunks) + " chunks of " + str(MAX_DAYS) + " days")

    for group in GROUPS:
        if group in BLACKLISTED_GROUPS:
            continue

        if not os.path.isdir(args.savePath + "/" + group):
            os.makedirs(args.savePath + "/" + group)

        for chunkIndex in range(nbBigChunks):
            chunkStartDate = startDate + timedelta(chunkIndex * (MAX_DAYS + 1))
            chunkEndDate = chunkStartDate + timedelta(MAX_DAYS)
            [sleepTime, strikes] = getChunk(chunkStartDate, chunkEndDate,
                                            chunkIndex, group, args, strikes,
                                            session)

            if sleepTime > 0:
                print("A problem occurred, adding a sleep to let it mellow")
                session.close()
                session = requests.Session()
                for timerIndex in range(sleepTime, 0, -1):
                    sys.stdout.write(str(timerIndex) + "... ")
                    sys.stdout.flush()
                    sleep(1)

        lastChunkStartDate = (startDate +
                              timedelta(nbBigChunks * (MAX_DAYS + 1)))
        lastChunkEndDate = lastChunkStartDate + timedelta(reste)
        getChunk(lastChunkStartDate, lastChunkEndDate, str(nbBigChunks),
                 group, args, strikes, session)

    session.close()


if __name__ == '__main__':
    main()
