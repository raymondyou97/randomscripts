#!/usr/bin/env python

"""
Notifies you if there is a covid vaccine appointment available by reverse engineering the vax4nyc endpoint which grabs all the covid appointments available
Have the site ready to immediately click and grab the time slot
You'll need to add the $cookie from the vax4nyc site and pip install playsound
"""

import requests
from time import time, sleep
from playsound import playsound

headers = {
    'authority': 'vax4nyc.nyc.gov',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'x-sfdc-page-scope-id': '6fd548a1-08cb-44df-b1d7-90a6200c8c57',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'x-sfdc-request-id': '77206110000e8ddff4',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept': '*/*',
    'origin': 'https://vax4nyc.nyc.gov',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://vax4nyc.nyc.gov/patient/s/vaccination-schedule',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
    # paste content of document.cookie here from https://vax4nyc.nyc.gov/patient/s/vaccination-schedule
    '$cookie': '',
}

params = (
    ('r', '9'),
    ('aura.ApexAction.execute', '1'),
)

data = {
  'message': '{"actions":[{"id":"90;a","descriptor":"aura://ApexActionController/ACTION$execute","callingDescriptor":"UNKNOWN","params":{"namespace":"","classname":"VCMS_BookAppointmentCtrl","method":"fetchDataWrapper","params":{"isOnPageLoad":false,"scheduleDate":"2021-03-21","zipCode":"11238","isSecondDose":false,"vaccineName":"","isReschedule":false,"isClinicPortal":false,"isCallCenter":false},"cacheable":false,"isContinuation":false}}]}',
  'aura.context': '{"mode":"PROD","fwuid":"Q8onN6EmJyGRC51_NSPc2A","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":"4cm95xKNoonR9yZ2JR2osw"},"dn":[],"globals":{},"uad":false}',
  'aura.pageURI': '/patient/s/vaccination-schedule',
  'aura.token': 'undefined'
}

def _get_appointments():
    response = requests.post('https://vax4nyc.nyc.gov/patient/s/sfsites/aura', headers=headers, params=params, data=data)
    return response.json()

def _check_if_desired_loc(resp, desired_loc):
    locs = resp["actions"][0]["returnValue"]["returnValue"]["lstMainWrapper"]
    all_locs = []
    for l in locs:
        center_name = l["lstDataWrapper"][0]["centerName"].lower()
        all_locs.append(center_name)
    print("found", all_locs)
    desired_loc = desired_loc.lower()
    return True in [True for l in all_locs if desired_loc in l]

def main():
    if not headers['$cookie']:
        raise Exception("MISSING COOKIE")

    retry_secs = 5
    while True:
        resp = _get_appointments()
        # the specific location you want.
        found = _check_if_desired_loc(resp, "Army Terminal")
        if found:
            print("found, playing lion roar")
            playsound('audio.mp3')
        else:
            print("not found. trying again in {} seconds".format(retry_secs))
        # check every 5 seconds. if you get rate limited, bump this up. but i doubt they have rate limiting capabilities here
        sleep(retry_secs - time() % retry_secs)

if __name__ == "__main__":
    main()
