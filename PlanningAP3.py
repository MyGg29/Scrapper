import requests, sys, re, locale
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event, vCalAddress, vText

url = "https://aurion-lille.isen.fr/faces/Planning.xhtml"
events = []
eventsData = []
eventsTeacher = []
eventsLocation = []

icalString = ""

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

with requests.Session() as s:
    r = s.get(url)
    print("Response URL: " + r.url)
    print("Cookies: " + str(s.cookies))

    parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
    payload = {"form": "form",
               "form:largeurDivCenter": "1142"}

    for DOMInput in parser.find_all("span", "rf-ddm-itm-lbl"):
        if "AP3" in DOMInput.get_text():
            payload[DOMInput.parent["id"]] = DOMInput.parent["id"]
    payload["javax.faces.ViewState"] = parser.select_one("#j_id1:javax.faces.ViewState:0")["value"]
    print("Payload: " + str(payload))
    r = s.post(url, params = payload)
    print("Response URL: " + r.url)
    parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
    print("Cookies: " + str(s.cookies))
    payload = {"form": "form",
               "form:largeurDivCenter": "1154",
               "form:j_idt263-value": "false",
               "form:calendarDebutInputDate": "09/10/2017",
               "form:calendarDebutInputCurrentDate": "10/2017",
               "form:calendarFinInputDate": "13/10/2017",
               "form:calendarFinInputCurrentDate": "10/2017",
               "form:dataTableFavori:j_idt150": "on",
               "form:dataTableFavori:0:j_idt151": "on",
               "javax.faces.source": "form:j_idt110",
               "javax.faces.partial.event": "click",
               "javax.faces.partial.execute": "form:j_idt110 @component",
               "javax.faces.partial.render": "@component",
               "org.richfaces.ajax.component": "form:j_idt110",
               "form:j_idt110": "form:j_idt110",
               "rfExt": "null",
               "AJAX:EVENTS_COUNT": "1",
               "javax.faces.partial.ajax": "true"}
    payload["javax.faces.ViewState"] = parser.select_one("#j_id1:javax.faces.ViewState:0")["value"]
    print("Payload: " + str(payload))
    r = s.post(r.url, params = payload)

    parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
    for DOMInput in parser.find_all("span", "ev_libelle"):
        if DOMInput.get_text() == "Du":
            classDate = DOMInput.parent.parent.parent.contents[3].get_text()
            classStartHour = DOMInput.parent.parent.parent.contents[7].get_text()
        if DOMInput.get_text() == "Au":
            classEndHour = DOMInput.parent.parent.parent.contents[7].get_text()
        if DOMInput.get_text() == "Matière":
            classLesson = DOMInput.parent.parent.parent.contents[3].get_text()
            eventsData.append({"startingTime": datetime.strptime(" ".join(classDate.split(" ")[1:]) + " " + classStartHour, "%d %B %Y %H:%M"),
                               "stoppingTime": datetime.strptime(" ".join(classDate.split(" ")[1:]) + " " + classEndHour, "%d %B %Y %H:%M"),
                               "title": classLesson})

    for DOMInput in parser.find_all("tr", id = re.compile(".*j_idt212:0")):
        classTeacherName = DOMInput.contents[0].get_text()
        classTeacherFirstname = DOMInput.contents[1].get_text()
        eventsTeacher.append({"teacher": classTeacherFirstname + " " + classTeacherName})

    for DOMInput in parser.find_all("td", id = re.compile(".*0:j_idt205")):
        eventsLocation.append({"location": DOMInput.get_text()})
        print(DOMInput.get_text())

    cal = Calendar()

    icalString += "BEGIN:VCALENDAR\r\n"

    for i in range(0, len(eventsData)):
        icalString += "BEGIN:VEVENT\r\n"
        events.append({**eventsData[i], **eventsTeacher[i], **eventsLocation[i]})
        calEvent = Event()
        calEvent['uid'] = i
        calEvent['dtstart'] = datetime.strftime(events[i]["startingTime"], "%Y%m%dT%H%M%S")
        calEvent['dtstamp'] = datetime.strftime(events[i]["startingTime"], "%Y%m%dT%H%M%S")
        calEvent['dtend'] = datetime.strftime(events[i]["stoppingTime"], "%Y%m%dT%H%M%S")
        calEvent['summary'] = events[i]["title"]
        calEvent['organizer'] = vCalAddress(events[i]["teacher"])
        calEvent['description'] = vCalAddress(events[i]["teacher"])
        calEvent['location'] = events[i]["location"]
        cal.add_component(calEvent)
        icalString += "UID:" + str(i) + "\r\n"
        icalString += "DTSTART:" + datetime.strftime(events[i]["startingTime"], "%Y%m%dT%H%M%S") + "\r\n"
        icalString += "DTEND:" + datetime.strftime(events[i]["stoppingTime"], "%Y%m%dT%H%M%S") + "\r\n"
        icalString += "SUMMARY:" + events[i]["title"] + "\r\n"
        icalString += "ORGANIZER:" + events[i]["teacher"] + "\r\n"
        icalString += "DESCRIPTION:" + events[i]["teacher"] + "\r\n"
        icalString += "LOCATION:" + events[i]["location"] + "\r\n"
        icalString += "END:VEVENT\r\n"

    icalString += "END:VCALENDAR\r\n"

    with open("calendar.ics", "wb") as f:
        f.write(cal.to_ical())

    with open("calendar2.ics", "w") as f:
        f.write(icalString)
    
    
