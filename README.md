# Scrapper
## Scraps ISEN's Aurion system

Pythons scripts to get the most out of ISEN's Aurion system.

### What there is so far ?

**CASLogin.py** : by editing the script to enter your username and password, you can connect a python-request session to the authentication system for the school system. Not used yet but could be useful someday.

**PlanningScrapper.py** : scraps the planning into an .ics file
Usage: `python3 PlanningAP3.py <year> [start date] [end date]`
Example: `python3 PlanningAP3.py AP3 09/10/2017 29/10/2017`
Outputs an .ics file in the current directory. This file can then be imported in Thunderbird/Lightning
