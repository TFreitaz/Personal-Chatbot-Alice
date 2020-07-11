import time
import datetime
import pickle
import os.path
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

path = "Calendar"

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(f"{path}/token.pickle"):
    with open(f"{path}/token.pickle", "rb") as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(f"{path}/credentials.json", SCOPES)
        creds = flow.run_local_server()
    # Save the credentials for the next run
    with open(f"{path}/token.pickle", "wb") as token:
        pickle.dump(creds, token)

service = build("calendar", "v3", credentials=creds)

urapython_id = ""  # Requires a particular google calendar id
holidays_id = "pt.brazilian#holiday@group.v.calendar.google.com"


def sep_time(t):
    if "T" in t:
        t = " ".join(t.split("T"))
    return t


def next_events(Id="primary"):
    myEvents = []
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = (
        service.events().list(calendarId=Id, timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime").execute()
    )
    events = events_result.get("items", [])
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        myEvents.append({"start": sep_time(start), "name": event["summary"]})
    return myEvents


def today_events(Id="primary"):
    myEvents = []

    now = time.localtime()
    day = now.tm_mday
    mon = now.tm_mon
    year = now.tm_year

    today = pd.to_datetime("{y}-{m}-{d}".format(y=year, m=mon, d=day))
    tomorrow = today + pd.to_timedelta(1, "d")

    today = datetime.datetime(year, mon, day).isoformat() + "Z"
    tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day).isoformat() + "Z"

    events_result = (
        service.events().list(calendarId=Id, timeMin=today, timeMax=tomorrow, singleEvents=True, orderBy="startTime").execute()
    )
    events = events_result.get("items", [])
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        myEvents.append({"start": sep_time(start), "name": event["summary"]})
    return myEvents
