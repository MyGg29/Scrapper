# Scrapper

### Scraps ISEN's Aurion system

Python package to get the most out of ISEN's Aurion system.  
Dependencies: python-requests python-beautifulsoup4

## Modules included:

### CASSession

Import this class to get a requests.Session() object which is connected to ISEN's session system and allows access to grades, rooms availability and personal planning.

You need your own credentials to use this class.

Usage example:
```python
from isen.CASSession import CASSession

session = CASSession()
session.setUsername("YOURUSERNAMEHERE")
session.setPassword("YOURPASSWORDHERE")

# Will throw and Exception if no password
# or username is set
with session as s:
    # Do things here that you would do with a normal
    # requests Session() object like s.get(url)
```

### PlanningScrapper

PlanningScrapper implements the functions to initialize a session with Aurion, retrieve a number of days of planning and store them.

Usage exemple:  
```python
from isen.PlanningScrapper import PlanningScrapper

planning = PlanningScrapper("AP3", "01/01/2018", "31/01/2018", "output")
planning.startSession()
planning.retrieveData()
planning.saveFiles()
planning.stopSession()
```

This snippet should get you a `output.ics` file in your local directory, containing the planning for the AP3 from 01/01/2018 to 31/01/2018.

## Scripts included:

Those should be stored in `/usr/bin` after installation. You can then call them as programs as they are probably in your PATH.

### GetPlanning.py

This script allows the retrieval of maximum 40 days of planning (the maximum allowed by Aurion).

```
usage: PlanningScrapper.py [-h] -g <group> [-s <start date>] [-e <end date>]
                           -o <filename> [-v] [-m] [-S] [-l] [-u <user>]
                           [-p <password>]

Scraps ISEN's planning website. Outputs an .ics file in the current directory.

optional arguments:
  -h, --help       show this help message and exit
  -g <group>       Set the group
  -s <start date>  Start day
  -e <end date>    End day
  -o <filename>    Name for the outputted file, without the extension
  -v               Verbose mode
  -m               Save the events in multiple files
  -S               Silent - disables all messages. Overwrites the -v (verbose)
                   argument.
  -l               Login - use login to get personalized planning
  -u <user>        User for the login
  -p <password>    Password for the login
  ```

Dependencies: python-requests python-beautifulsoup4

### GetAllPlannings.py

A script that will be used on a CalDAV server to regularly update all plannings for all groups.

```
usage: GetAllPlannings.py
```

### RoomsExtractor.py

```
usage: RoomsExtractor.py [-h] -u <username> -p <password> -o <filename>

Gets ISEN's classrooms availability in CSV. Outputs a .csv file in the current
directory.

optional arguments:
  -h, --help     show this help message and exit
  -u <username>  Username
  -p <password>  Password
  -o <filename>  Name for the outputted file, without the extension
```

### What to install and how ?

The planning scrapper and all its tools and services can be installed through the makefile. Using `sudo make install` should install all the python scripts in `/usr/share/isen/planning-scrapper/` and all the services files in `/usr/lib/systemd/system/`.
