import os
import random
import time

from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import csv

from download import download_position_lookup_latest
from extract import get_latest_jobs
from settings import sleep_interval, test_url, get_latest_positions_from_s3
from setup import chat_db, output

begin = [
    "Hi! I'm JobAssistant, your friendly AI assistant. I'm here to help land you a job! To begin, please copy and paste the entire job ad including the position title and everyting under it. If you don't have a full job ad, just type the title of the position."
]

ask_org = [
    "Can you please type the company name?",
    "What's the name of the company you're applying for?",
    "What company are you applying for?"
]

ask_person = [
    "Who is the person this cover letter is addressed to? Please type 'skip' if you don't know who the letter is addressed to.",
    "What's the employer's name or the name of the contact the cover letter will be addressed to? Please type 'skip' if you don't know who it's address to."
]

user_fullname = [
    "What's your full name?",
    "Please type your full name.",
    "Please provide your full name."
]

work_for = "You want to work for"

# errors
wrong_jobtitle = [
    "Can you please try typing the job title again please? Perhaps try a variation of that position.",
    "Sorry but I don't understand what you put in for job position. Can you check the position or please try a variation of the job title?",
    "Please check the position. You might want to try another variation of the job title so you can help me understand better."
]

full_fail = ['Sorry, something went wrong. Please try again.', ' Something went wrong. Please start a new chat.', 'Something went wrong. Please start a new chat.']
only_job = "Please type only the job position."

currently_dont_support = [
    "Unfortunately, at the moment, I don't write for that position.",
    "Sorry but currently I don't support that position."
]

# success
success_basic = "your cover letter so far"


# error_2 = "What's the employer's name or the name of the contact the cover letter will be addressed to? Please type 'skip' if you don't know who it's address to."
def click_correct(driver_in):
    all_buttons = driver_in.find_elements_by_class_name("option")
    for i in all_buttons:
        if i.text == "correct":
            i.click()


def check_for_fail(message):
    if message in wrong_jobtitle or message in currently_dont_support or message in full_fail:
        status = True
    else:
        status = False
    return status


def get_last_message(driver_in, counter_in):
    replies = driver_in.find_elements_by_css_selector(".message.to.ready")
    print(len(replies))
    print("text:", replies[-1].text)
    while len(replies) is not counter_in or replies[-1].text == " ":
        print("not ready")
        replies = driver_in.find_elements_by_css_selector(".message.to.ready")
    last_message = replies[-1].text
    print("LAST MESSAGE:",last_message)
    print(len(replies))
    return last_message


def respond(driver_in, last_message, job_in, company_in, contact_in, full_name_in, chat_db_path):
    no_match = False
    success = False

    if last_message in begin:
        driver_in.find_element_by_id("userInput").send_keys(job_in)
        driver_in.find_element_by_id("userInput").send_keys(Keys.ENTER)
        chosen_message = job_in
    elif last_message in ask_org:
        driver_in.find_element_by_id("userInput").send_keys(company_in)
        driver_in.find_element_by_id("userInput").send_keys(Keys.ENTER)
        chosen_message = company_in
    elif last_message in ask_person:
        driver_in.find_element_by_id("userInput").send_keys(contact_in)
        driver_in.find_element_by_id("userInput").send_keys(Keys.ENTER)
        chosen_message = contact_in
    elif last_message in user_fullname:
        driver_in.find_element_by_id("userInput").send_keys(full_name_in)
        driver_in.find_element_by_id("userInput").send_keys(Keys.ENTER)
        chosen_message = full_name_in
    elif work_for in last_message:
        driver_in.find_element_by_class_name("option").click()
        chosen_message = 'CORRECT'
    elif last_message == only_job:
        driver_in.find_element_by_id("userInput").send_keys(job_in)
        driver_in.find_element_by_id("userInput").send_keys(Keys.ENTER)
        chosen_message = job_in
    elif success_basic in last_message:
        chosen_message = ""
        success = True
    else:
        no_match = True
        print("no match:", last_message)
        input("NO MATCH!")

        return no_match, success

    if chosen_message:
        with open(chat_db_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user_type', 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'user_type': 'USER', 'message': chosen_message})

    return no_match, success


def test_job(job_in, company_in, contact_in, full_name_in, driver_in, sleep_int):
    driver_in.get(test_url)
    driver_in.find_element_by_id("start-chat-btn2").click()
    print("SLEEPing")
    time.sleep(5)
    driver_in.execute_script("window.onbeforeunload = function() {};")
    driver_in.execute_script("window.alert = function() {};")
    chat_db_path = chat_db(job_in)
    continue_chat = True
    counter = 0
    while continue_chat:
        counter += 1
        last_message = get_last_message(driver_in, counter)
        failed = check_for_fail(last_message)
        with open(chat_db_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user_type', 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'user_type': 'BOT', 'message': last_message})

        if failed:
            with open('output.csv', 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['job', 'status', 'last_response']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(
                    {
                        'job': job_in,
                        'last_response': last_message,
                        'status': 'FAILED'
                    }
                )
            break

        no_match, success = respond(driver_in, last_message, job_in, company_in, contact_in, full_name_in, chat_db_path)
        if no_match:
            break

        if success:
            with open('output.csv', 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['job', 'status', 'last_response']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writerow(
                    {
                        'job': job_in,
                        'last_response': last_message,
                        'status': 'SUCCESS'
                    }
                )

            break
        time.sleep(sleep_int)

def remove_old():
    for filename in tqdm(os.listdir("chats")):
        if filename.endswith(".csv"):
            dest_path = os.path.join("chats", filename)
            os.remove(dest_path)

def run():
    output()
    remove_old()
    if get_latest_positions_from_s3:
        download_position_lookup_latest()
    time.sleep(1)
    latest_jobs = get_latest_jobs()

    company_in = "Microsoft"
    contact_in = "Laura Jones"
    full_name_in = "Sarah Lior"

    option = Options()
    option.add_argument("--headless")
    driver = webdriver.Chrome(options=option)

    for job in tqdm(latest_jobs):
        test_job(job, company_in, contact_in, full_name_in, driver, sleep_interval)

    driver.close()
    driver.quit()


run()
