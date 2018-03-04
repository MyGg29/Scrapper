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

This snippet should get you a `output.ics` file in your local directory, containing the planning for the AP3 from 01/01/2017 to 31/01/2018.

## Scripts included:

Those should be stored in `/usr/bin` after installation. You can then call them as programs as they are probably in your PATH.

### GetPlanning.py

This script allows the retrieval of maximum 40 days of planning (the maximum allowed by Aurion).

```
usage: PlanningScrapper.py [-h] [-s <start date>] [-e <end date>] [-v] [-m]
                           [-S] [-l] [-u <user>] [-p <password>]
                           <group> <filename>

Scraps ISEN's planning website. Outputs an .ics file in the current directory.

positional arguments:
  <group>          Set the group
  <filename>       Name for the outputted file, without the extension

optional arguments:
  -h, --help       show this help message and exit
  -s <start date>  Start day
  -e <end date>    End day
  -v               Verbose mode
  -m               Save the events in multiple files
  -S               Silent - disables all messages. Overwrites the -v (verbose)
                   argument.
  -l               Login - use login to get personalized planning
  -u <user>        User for the login
  -p <password>    Password for the login
  ```

### GetAllPlannings.py

A script that will be used on a CalDAV server to regularly update all plannings for all groups.

```
usage: GetAllPlanning.py [-h] [-c <conf_file>] [-v] [-m] [-S] [-l] [-u <user>]
                         [-p <password>] [-P <files_path>] [-L <log_path]

Gets all ISEN's plannings and save them in a folder in ical format.

optional arguments:
  -h, --help       show this help message and exit
  -c <conf_file>   Configuration file
  -v               Verbose mode
  -m               Save the events in multiple files
  -S               Silent - disables all messages. Overwrites the -v (verbose)
                   argument.
  -l               Enable login
  -u <user>        User for the login
  -p <password>    Password for the login
  -P <files_path>  The path where to save the files that have been retrieved
  -L <log_path     The path where to save the log file
```

Arguments that are not given default to the one given in the configuration file that can be found in `/etc/isen-planning.conf` or by the `-c` argument.

### RoomsExtractor.py

```
usage: RoomsExtractor.py [-h] <user> <password> <filename>

Gets ISEN's classrooms availability in CSV. Outputs a .csv file in the current
directory.

positional arguments:
  <user>      User for the login
  <password>  Password for the login
  <filename>  Name for the outputted file, without the extension

optional arguments:
  -h, --help  show this help message and exit
```

### GradesExtractor.py

```
usage: GradesExtractor.py [-h] <user> <password> <filename>

Gets grades in CSV. Outputs a .csv file in the current directory.

positional arguments:
  <user>      User for the login
  <password>  Password for the login
  <filename>  Name for the outputted file, without the extension

optional arguments:
  -h, --help  show this help message and exit
```

## Installation

Start by cloning this repository using `git clone https://github.com/MyGg29/Scrapper.git`. You can then go in the newly created folder and launch `setup.py install` from here. If you don't have the rights to install it, launch it with `sudo` or add it to your local user by adding the parameter `--user` to the install command. If you do choose to install it for your user, you'll need to add `~/.local/bin` to your PATH to be able to launch the scripts. However, using the modules in your own script should work out of the box.
