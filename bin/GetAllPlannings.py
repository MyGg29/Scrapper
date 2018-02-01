#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from time import sleep
import os
from isen.PlanningScrapper import PlanningScrapper

MAX_DAYS = 40
GROUPS = ["AP3", "AP4", "AP5", "CIR1", "CIR2", "CIR3", "CPG1", "CPG2", "CSI3",
          "CSIU3", "M1", "M2"]

# Those are blacklisted group because we don't handle them yet, see
# PlanningScrapper.py for more information
BLACKLISTED_GROUPS = ["CIR1", "CIR2", "CIR3", "CPG1", "CPG2", "CSI3", "CSIU3",
                      "M1", "M2"]


def getChunk(startDate, endDate, chunkIndex, group):
    planning = PlanningScrapper(
        group=group,
        output=group + "/" + str(chunkIndex),
        startDate=datetime.strftime(startDate, "%d/%m/%Y"),
        endDate=datetime.strftime(endDate, "%d/%m/%Y"),
        multiple=True,
        silent=True,
    )

    if not planning.startSession():
        print("\x1B[31;40m" + "FAILURE" + "\x1B[0m")
        return False

    if not planning.retrieveData():
        print("\x1B[31;40m" + "FAILURE" + "\x1B[0m")
        return False

    planning.saveFiles()
    planning.stopSession()
    print("\x1B[32;40m" + "SUCCESS" + "\x1B[0m")
    return True


def main():
    startDate = datetime(year=2017, month=9, day=1)
    endDate = datetime(year=2018, month=6, day=24)

    totalDays = (endDate - startDate).days
    nbBigChunks = totalDays // MAX_DAYS
    reste = totalDays % MAX_DAYS

    print("We need to get " + str(totalDays) + " days in " +
          str(nbBigChunks) + " chunks of " + str(MAX_DAYS) + " days")

    for group in GROUPS:
        if group in BLACKLISTED_GROUPS:
            continue

        if os.path.isdir("./" + group):
            for rmFile in os.listdir(group):
                os.remove(group + "/" + rmFile)
            os.removedirs(group)
        os.mkdir("./" + group)

        for chunkIndex in range(nbBigChunks):
            chunkStartDate = startDate + timedelta(chunkIndex * MAX_DAYS)
            chunkEndDate = startDate + timedelta((chunkIndex + 1) * MAX_DAYS)
            getChunk(chunkStartDate, chunkEndDate, chunkIndex, group)

            print("Waiting a little bit before getting next chunk")
            sleep(5)

        lastChunkStartDate = startDate + timedelta(nbBigChunks * MAX_DAYS)
        lastChunkEndDate = lastChunkStartDate + reste
        getChunk(lastChunkStartDate, lastChunkEndDate, str(nbBigChunks), group)


if __name__ == '__main__':
    main()
