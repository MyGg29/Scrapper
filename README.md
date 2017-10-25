# Scrapper
## Scraps ISEN's Aurion system

Pythons scripts to get the most out of ISEN's Aurion system.

### What is there so far ?

#### CASSession.py

Import this class to get a requests.Session() object which is connected to ISEN's session system and allows access to grades, rooms availability and probably more.

You need your own credentials to use this class.

Usage example:
```python
import CASSession

session = CASSession()
session.setUsername("YOURUSERNAMEHERE")
session.setPassword("YOURPASSWORDHERE")

# Will throw and Exception if no password
# or username is set
with session as s:
    # Do things here that you would do with a normal
    # requests Session() object like s.get(url)
```

Dependencies: python-requests python-beautifulsoup4

#### PlanningScrapper.py

```
usage: python3 PlanningScrapper.py [-h] -g <group> [-s <start date>]
                                   [-e <end date>] -o <filename>

Scraps ISEN's planning website. Outputs an .ics file in the current directory.

optional arguments:
  -h, --help       show this help message and exit
  -g <group>       Set the group
  -s <start date>  Start day
  -e <end date>    End day
  -o <filename>    Name for the outputted file, without the extension
  -v               Verbose mode
  ```

Dependencies: python-requests python-beautifulsoup4

#### RoomsExtractor.py

```
usage: python3 RoomsExtractor.py [-h] -u <username> -p <password> -o
                                 <filename>

Gets ISEN's classrooms availability in CSV. Outputs a .csv file in the
current directory.

optional arguments:
  -h, --help     show this help message and exit
  -u <username>  Username
  -p <password>  Password
  -o <filename>  Name for the outputted file, without the extension
```

Dependencies: python-requests python-beautifulsoup4 CASsession.py
