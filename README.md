# Scrapper
## Scraps ISEN's Aurion system

Pythons scripts to get the most out of ISEN's Aurion system.

### What is there so far ?

#### CASLogin.py

By editing the script to enter your username and password, you can connect a python-request session to the authentication system for the school system. Not used yet but could be useful someday.

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
  ```

Dependencies: python-requests python-beautifulsoup4
