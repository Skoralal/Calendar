from bs4 import BeautifulSoup
import codecs
import datetime as dt
from datetime import date
import calendar
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

SCOPES = ["https://www.googleapis.com/auth/calendar"]




with codecs.open("C:\prog_questionmark\Calendar\html\\ver2.html", "r", "utf_8_sig") as html_file:
    content = html_file.read()




class day:
    def __init__(self, lessons) -> None:
        self.week_day = lessons[0]
        self.lessons = lessons[2:]

    def day_print(self):
        return self.lessons
    
    def get_week_day(self):
        return self.week_day
    

class lesson:
    def __init__(self, input_str) -> None:
        input = []
        in_init = BeautifulSoup(str(input_str), "lxml")
        input = in_init.find_all("td")
        self.time = input[0].text
        self.name = input[1].text     
        self.type = input[2].text
        self.repeat = input[3].text
        self.room = input[4].text
        self.teacher = input[5].text
    
    def lesson_print(self):
        return [self.time, self.name, self.type, self.repeat, self.room, self.teacher]

soup = BeautifulSoup(content, "lxml")
timetable = soup.find_all("table", class_="timetable")
prep1 = soup.find_all("tr")
prep1 = prep1[6:]
aboba = lesson(prep1[7])
# print(aboba.lesson_print())
# print(prep1)

days = []
table = []
for i, da_y in enumerate(prep1):
    if "th colspan=" in str(da_y):
        if i != 0:
            days.append(day(table))
        table.clear()
        table.append(da_y.text)
    try:
        table.append(lesson(da_y))
    except:
        None
    
translate = {
    "Понедельник": "Monday",
    "Вторник": "Tuesday",
    "Среда": "Wednesday",
    "Четверг": "Thursday",
    "Пятница": "Friday",
    "Суббота": "Saturday",
    "Воскресение": "Sunday"
}


# print(len(days))
# print(days[0][1].lesson_print())
# print(days[1].day_print()[0].lesson_print())
for value in days:
    for val in value.day_print():
        print(val.lesson_print(), translate[f"{value.get_week_day()}"])

# print(calendar.day_name[date.today().weekday()])   
# print(date.today().year)
# print(date.today()<date.today())

def get_week(input):
    dic = {
        "Monday": "",
        "Tuesday": "",
        "Wednesday": "",
        "Thursday": "",
        "Friday": "",
        "Saturday": "",
        "Sunday": ""
    }
    znam = dic.copy()
    dic[f"{calendar.day_name[input.weekday()]}"] = str(input)
    # print(dic)
    # print(input.isoweekday())
    monday = input - dt.timedelta(days=input.isoweekday()-1)
    dic["Monday"] = str(input - dt.timedelta(days=input.isocalendar().weekday))
    for i, value in enumerate(dic):
        dic[value] = str(monday + dt.timedelta(days=i))
        znam[value] = str(monday + dt.timedelta(days=i+7))
    return [dic, znam]
    



def chis_znam():
    output = None
    # 2 lists, one with dates of chis and the other with znams as starts of events
    last_sep_date = None
    if date(date.today().year, 9, 1) > date.today():
        last_sep_date = date(date.today().year-1, 9, 1)
    else:
        last_sep_date = date(date.today().year, 9, 1)

    # last_sep_date = date(2024,9,1)


    # print(calendar.day_name[last_sep_date.weekday()])
    while calendar.day_name[last_sep_date.weekday()] in ["Saturday", "Sunday"]:
        # print(222)
        last_sep_date = last_sep_date + dt.timedelta(days=1)
    # print(last_sep_date)

    return last_sep_date



def prep(input, week_day):
    znam = get_week(chis_znam())[0]
    chis = get_week(chis_znam())[1]
    interval = input[3]
    print(interval)
    dic = {
            "summary": f"{input[4]} {input[1]}",
            "location": "",
            "description": "",
            "colorID": 6,
            "start": {
                "dateTime": f"2023-06-29T{input[0][:5]}:00+03:00",
                "timeZone": "Europe/Moscow"
            },
            "end": {
                "dateTime": f"2023-06-29T{input[0][8:]}:00+03:00",
                "timeZone": "Europe/Moscow"
            },
            "recurrence":[
                "RRULE:FREQ=WEEKLY;INTERVAL=2"
            ],
            "attendees": [
                {"email": "skoralal4@gmail.com"}
            ],
        }
    if interval == "Еженедельно":
        dic["recurrence"] =[
                "RRULE:FREQ=WEEKLY;INTERVAL=1"
            ]
        dic["start"] = {
                "dateTime": f"{str(chis[week_day])}T{input[0][:5]}:00+03:00",
                "timeZone": "Europe/Moscow"
            }
        dic["end"] = {
                "dateTime": f"{str(chis[week_day])}T{input[0][8:]}:00+03:00",
                "timeZone": "Europe/Moscow"
            }
        
    if interval == "Числитель":
        dic["recurrence"] =[
                "RRULE:FREQ=WEEKLY;INTERVAL=2"
            ]
        dic["start"] = {
                "dateTime": f"{chis[week_day]}T{input[0][:5]}:00+03:00",
                "timeZone": "Europe/Moscow"
            }
        dic["end"] = {
                "dateTime": f"{chis[week_day]}T{input[0][8:]}:00+03:00",
                "timeZone": "Europe/Moscow"
            }
        
    if interval == "Знаменатель":
        dic["recurrence"] =[
                "RRULE:FREQ=WEEKLY;INTERVAL=2"
            ]
        dic["start"] = {
                "dateTime": f"{znam[week_day]}T{input[0][:5]}:00+03:00",
                "timeZone": "Europe/Moscow"
            }
        dic["end"] = {
                "dateTime": f"{znam[week_day]}T{input[0][8:]}:00+03:00",
                "timeZone": "Europe/Moscow"
            }
    return dic

def goog():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("C:\prog_questionmark\Calendar\keys\key.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        event_result = service.events().list(calendarId="primary", timeMin = now, maxResults=10, singleEvents=True, orderBy="startTime").execute()
        events = event_result.get("items", [])

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            # print(start, event)

        mevent = {
            "summary": "Name",
            "location": "place",
            "description": "description",
            "colorID": 6,
            "start": {
                "dateTime": "2023-06-29T09:00:00+03:00",
                "timeZone": "Europe/Moscow"
            },
            "end": {
                "dateTime": "2023-06-29T10:30:00+03:00",
                "timeZone": "Europe/Moscow"
            },
            "recurrence":[
                "RRULE:FREQ=WEEKLY;INTERVAL=2"
            ],
            "attendees": [
                {"email": "skoralal4@gmail.com"}
            ],
            
            
        }

        

        # recurring_event = service.events().insert(calendarId='primary', body=mevent).execute()
        amogus = service.events().insert(calendarId='primary', body=prep(days[0].day_print()[1].lesson_print(), translate[f"{days[0].get_week_day()}"])).execute()
        for value in days:
            for val in value.day_print():
                print(value, val)
                amogus = service.events().insert(calendarId='primary', body=prep(val.lesson_print(), translate[f"{value.get_week_day()}"])).execute()

    except HttpError as error:
        print("eerroorr", error)

if __name__ == "__main__":
    goog()
    chis_znam()