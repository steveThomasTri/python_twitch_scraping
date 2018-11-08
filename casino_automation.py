from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import csv
import time
import datetime

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def scheduled_job():
    print('This job is run every weekday at 10am.')

@sched.scheduled_job('cron', day_of_week='mon-fri', minute='*/15')
def scheduled_jobd():
    snapshot_date = datetime.datetime.now()
    page_link = "https://www.twitch.tv/directory/game/Casino"
    browser = webdriver.Chrome(executable_path=r'C:/selenium/chromedriver.exe')
    browser.maximize_window()
    browser.get(page_link)
    time.sleep(10)

    SCROLL_PAUSE_TIME = 5

    # Get scroll height
    original_scroll_length = 0

    while True:
        scroll = browser.find_elements_by_css_selector("div.preview-card")
        scroll_length = len(scroll)
        browser.execute_script("arguments[0].scrollIntoView();", scroll[len(scroll) -1])

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        if original_scroll_length == scroll_length:
            break
        original_scroll_length = scroll_length

    with open("twitch_casino.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for streamer in scroll:
            writer.writerow([str(datetime.datetime.now().strftime("%b %d %y")),str(datetime.datetime.now().strftime("%H")),str(datetime.datetime.now().strftime("%M")),streamer.text.split("\n")[3],streamer.text.split("\n")[1].replace(" viewers", "").replace(",",""),streamer.text.split("\n")[-1]])

sched.start()