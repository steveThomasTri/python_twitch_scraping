from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import csv
import time
import datetime

import requests
import json

import os.path

from config import client_id

def new_page(n):
    params = (
        ('game_id', game_id),('first','100'),("after",n),
    )
    response2 = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)
    
    if(len(response2.json()["data"]) > 0):
        try:
            streams_arr.append(response2.json())
            # print(response2.json()["pagination"]['cursor'])
            new_page(response2.json()["pagination"]['cursor'])
        except KeyError:
            print("Error... Waiting")
            time.sleep(25)
            new_page(response2.json()["pagination"]['cursor'])

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def scheduled_job():
    print('This job is run every weekday at 10am.')

@sched.scheduled_job('cron', day_of_week='mon-fri', minute='*/15')
def scheduled_jobd():
    streams_arr = []
    game_id = 504462
    game_name = "Call of Duty: Black Ops 4"

    #First results
    headers = {
        'Client-ID': client_id,
    }

    params = (
        ('game_id', game_id),('first','100'),
    )

    response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)

    streams_arr.append(response.json())

    new_page(response.json()["pagination"]['cursor'])

    counter = 0
    viewercount = 0
    filename = "resources/"+game_name+".csv"
    filename2 = "resources/"+game_name+"-total.csv"
    file_exists = os.path.isfile(filename)
    file_exists2 = os.path.isfile(filename2)

    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            writer.writerow(["date", "hour", "minute", "user_id", "user_name", "title", "viewer_count", "stream_start_date","seconds_since_stream","language"])
            
        for streamer in streams_arr:
            for row in streamer["data"]:
                counter += 1
                viewercount += row["viewer_count"]
                writer.writerow([str(datetime.datetime.now().strftime("%b %d %y")), \
                                str(datetime.datetime.now().strftime("%H")), \
                                str(datetime.datetime.now().strftime("%M")), \
                                row["user_id"], row["user_name"], row["title"], \
                                row["viewer_count"], \
                                (datetime.datetime.strptime(row["started_at"],"%Y-%m-%dT%H:%M:%SZ") - datetime.timedelta(hours=5)).strftime("%b %d %Y %-I:%M%P"), \
                                round((datetime.datetime.today()-(datetime.datetime.strptime(row["started_at"],"%Y-%m-%dT%H:%M:%SZ") - datetime.timedelta(hours=5))).total_seconds()), \
                                row["language"]])
            
    with open(filename2, "a", newline="") as csvfile2:
        writer2 = csv.writer(csvfile2)
        
        if not file_exists2:
            writer2.writerow(["date_int","date_string","number_of_streamers", "total_viewers"])
        
        writer2.writerow([int(datetime.datetime.today().strftime('%s')),datetime.datetime.today().strftime("%b %d %Y %-I:%M%P"),counter,viewercount])

sched.start()