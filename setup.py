#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name="isen",
    packages=["isen"],
    version="0.0.1",
    requires=["bs4", "requests"],
    author="Rodolphe Houdas",
    author_email="NoMail",
    description="Tools to get the most out of ISEN's online tools",
    url="https://github.com/MyGg29/Scrapper",
    download_url="https://github.com/MyGg29/Scrapper/archive/master.zip",
    license="Beerware",
    scripts=["bin/GetPlanning.py",
             "bin/GetAllPlannings.py",
             "bin/RoomsExtractor.py",
             "bin/GradesExtractor.py"],
    data_files=[('/etc', ['etc/isen-planning.conf'])],
    # La liste ici : https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        ],
    long_description="Short description for now"
)
