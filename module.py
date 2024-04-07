# os
import os.path

# mongodb
import pymongo
from bson.json_util import dumps, loads 

# gcalendar api
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# data processing
import pandas as pd
import numpy as np
from datetime import datetime

# ----- pymongo setting -----

path = '../event_site_project_access/mongodb_access.txt'
f = open(path, 'r')
mongo_access = f.read()
f.close()
client = pymongo.MongoClient(mongo_access)

# ----- db & collection setting -----

db = client['event_site']
event_info_collection = db['event_information']
space_info_collection = db['space_information']
event_tag_collection = db['event_tag']

# ----- google calendar setting ----- 

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

'''
creds = None
if os.path.exists('../event_site_project_access/token.json'):
    creds = Credentials.from_authorized_user_file('../event_site_project_access/token.json', SCOPES)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file('../event_site_project_access/credentials.json', SCOPES)
    creds = flow.run_local_server(port = 0)
    with open('../event_site_project_access/token.json', 'w') as token:
        token.write(creds.to_json())
'''

creds = service_account.Credentials.from_service_account_file(
    '../event_site_project_access/service_account_credentials.json',
    scopes = SCOPES
)

try:
    service = build('calendar', 'v3', credentials = creds)
except HttpError as error:
    print('An error occurred: %s' % error)

# ----- choosed calendar setting ----- 

calendarId = '62c2d3e83153931e66c3b91b3edcecad88eb8fa2c0df6f8a1fa74d6d765c16be@group.calendar.google.com'



# ----- build event function ----- 

def build_event(**kwargs): 
    '''
    Input the collection and kwargs to building events in the target DB and google calendar. 
    - kwargs: event information dictionary which includes event_name, event_bgn_time, event_end_time, event_location, event_host
    '''
    # create a dict to put event info into google calendar
    gevent_info = {
    'summary': kwargs['event_name'], 
    'location': kwargs['event_location'], 
    'start': {
        'dateTime': kwargs['event_bgn_time'].isoformat('T'), 
        'timeZone': 'Asia/Taipei', 
    }, 
    'end': {
        'dateTime': kwargs['event_end_time'].isoformat('T'), 
        'timeZone': 'Asia/Taipei', 
    }, 
    'reminders': {
        'useDefault': False, 
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    }, 
    }
    event = service.events().insert(calendarId = calendarId, body = gevent_info).execute()
    print('Event created: %s' % (event.get('htmlLink')), ', ', 'id: %s' % (event.get('id')))

    gcalendar_id = event.get('id')

    # create a dict to put event info into DB
    try: 
        max_event_id = event_info_collection.find_one(sort = [('event_id', -1)])['event_id']
    except:
        max_event_id = 0
    event_id_allocate = max_event_id + 1
    info = {'event_id': event_id_allocate, 'gcalendar_id': gcalendar_id}
    for k, v in kwargs.items(): 
        info[k] = v
    info['updt_date'] = datetime.now()
    event_info_collection.insert_many([info])
    print('Event inserted to mongodb. ')

    # event_tag
    if kwargs.get('tag'):
        for tag in kwargs['tag']:
            if event_tag_collection.find({'tag': tag}).distinct('event_id'):
                event_tag_collection.update_one({'tag': tag}, {'$push': {'event_id': event_id_allocate}})
            else:
                event_tag_collection.insert_one({'tag': tag, 'event_id': [event_id_allocate]})


# ----- add attendees function ----- 

def add_attendees(gcalendar_id, attendee_email):
    # get the target event in google calendar
    event = service.events().get(calendarId = calendarId, eventId = gcalendar_id).execute()

    # get the current attendees list and add new attendee
    try: 
        attendees_list = event['attendees']
    except: 
        attendees_list = []
    attendees_list.append({'email': attendee_email})

    # update the attendees list
    event['attendees'] = attendees_list
    updated_event = service.events().update(calendarId = calendarId, eventId = event['id'], body = event).execute()

    # print the new attendees list
    get_updated_event = service.events().get(calendarId = calendarId, eventId = event['id']).execute()
    print('Update attendees, new attendees list became ', get_updated_event['attendees'])

# ----- build space function ----- 
def build_space(**kwargs): 
    '''
    Input the collection and kwargs to building events space in the target DB. 
    - kwargs: space_name, space_capacity, type
    '''
    # create a dict to put info into DB
    try: 
        max_space_id = space_info_collection.find_one(sort = [('space_id', -1)])['space_id']
    except:
        max_space_id = 0

    space_info = {
    'space_id': max_space_id + 1, 
    'space_name': kwargs['space_name'], 
    'space_capacity': kwargs['space_capacity'], 
    'type': kwargs['type'], 
    'updt_date': datetime.now(), 
    }

    space_info_collection.insert_many([space_info])
    print('Space info inserted to mongodb. ')