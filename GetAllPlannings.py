#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from subprocess import call
from time import sleep
import os

MAX_DAYS = 40
GROUPS = ["AP3", "AP4", "AP5", "CIR1", "CIR2", "CIR3", "CPG1", "CPG2", "CSI3", "CSIU3", "M1", "M2"]

# Those are blacklisted group because we don't handle them yet, see PlanningScrapper.py for more information
BLACKLISTED_GROUPS = ["CIR1", "CIR2", "CIR3", "CPG1", "CPG2", "CSI3", "CSIU3", "M1", "M2"]

if __name__ == '__main__':
    startDate = datetime(year=2017, month=9, day=1)
    endDate = datetime(year=2018, month=6, day=24)

    totalDays = (endDate - startDate).days
    nbBigChunks = totalDays // MAX_DAYS
    reste = totalDays % MAX_DAYS

    print("We need to get " + str(totalDays) + " days in " + str(nbBigChunks) + " chunks of " + str(MAX_DAYS) + " days")

    for group in GROUPS:
        if group in BLACKLISTED_GROUPS:
            continue

        if os.path.isdir("./" + group):
            for rmFile in os.listdir(group):
                os.remove(group + "/" + rmFile)
            os.removedirs(group)
        os.mkdir("./" + group)

        for chunkIndex in range(nbBigChunks):
            indexOffset = len(os.listdir("./" + group))
            chunkStartDate = startDate + timedelta(days = chunkIndex * MAX_DAYS)
            chunkEndDate = startDate + timedelta(days = (chunkIndex + 1) * MAX_DAYS)

            call(["python", "PlanningScrapper.py", "-g", group, "-o", group + "/" + str(chunkIndex), "-s", datetime.strftime(chunkStartDate, "%d/%m/%Y"), "-e", datetime.strftime(chunkEndDate, "%d/%m/%Y"), "-m"])

            print("Waiting a little bit before getting next chunk")
            sleep(5)

        lastChunkStartDate = startDate + timedelta(days = nbBigChunks * MAX_DAYS)
        lastChunkEndDate = startDate + timedelta(days = nbBigChunks * MAX_DAYS + reste)

        call(["python", "PlanningScrapper.py", "-g", group, "-o", group + "/test" + str(nbBigChunks), "-s", datetime.strftime(lastChunkStartDate, "%d/%m/%Y"), "-e", datetime.strftime(lastChunkEndDate, "%d/%m/%Y"), "-m"])
