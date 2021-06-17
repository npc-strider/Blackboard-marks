
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# For chrome stuff
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
# ---
from urllib.parse import parse_qs, urlparse
import os
import requests
import time
import getpass
import json
import re
import sys
import argparse
import pathlib

import utils.selectors
from utils.asset import Asset, RequestStack
from utils.wait import SwitchToIFrame, WaitClickable, WaitDiv
from constants.constants import BASE_URL
from utils.login import login
from utils.selectors import Selectors
from utils.utils import friendly_filename, get_assignment_name, get_text_excluding_children, save_html
import code
from random import randint

testing = False
try:
    testing = True
    from utils.test import get_etc  
except:
    def get_etc(*args): return False

cookie = None

def click_the_fing_button(driver,button):
    # https://stackoverflow.com/a/67414801 stupid bug
    try:
        ActionChains(driver).move_to_element(button)
        ActionChains(driver).click(button).perform()
        WebDriverWait(driver,2).until(EC.number_of_windows_to_be(2))
    except:
        driver.set_window_size(1024, 768)   # hack to wake selenium up when it doesnt want to click the button!
        click_the_fing_button(driver,button)
        driver.maximize_window()

# You can probably replace this with a recursive method like in blackboard scraper but tbh i just want to get this script done so i can stop working for once.
def scrape_further(driver,path):
    # attempts for bb-held tests
    attempts = driver.find_elements_by_xpath("//a[starts-with(@href, '/webapps/assessment')]")
    attempts = [ x.get_attribute('href') for x in attempts ]
    for i, attempt in enumerate(attempts):
        name = "attempt_"+str(i)+"_["+parse_qs(urlparse(attempt).query)['attempt_id'][0]+"]"
        attempt = re.sub("^"+BASE_URL,"",attempt)
        driver.execute_script("window.open('"+BASE_URL+attempt+"')")
        WebDriverWait(driver,10).until(EC.number_of_windows_to_be(3))
        driver.switch_to.window(driver.window_handles[2])
        save_html(path, name, driver.page_source)
        if testing:
            get_etc(driver, cookie, path)
        driver.close()
        driver.switch_to.window(driver.window_handles[1])

    # submission file for assignment
    request_stack = RequestStack(cookie)
    attempts = driver.find_elements_by_xpath("//a[starts-with(@href, '/webapps/assignment/download')]")
    attempts = [ x.get_attribute('href') for x in attempts ]
    for i, attempt in enumerate(attempts):
        request_stack.add_file(attempt,path)
    request_stack.download_all()

parser = argparse.ArgumentParser(description='Automated microsoft SSO login.')
# parser.add_argument("-p", "--password", help="Automatically use provided password", default="")
parser.add_argument("-u", "--username", help="Automatically use provided userID", default="")

args = parser.parse_args()

CAPABILITIES = DesiredCapabilities.CHROME
CAPABILITIES['goog:loggingPrefs'] = {'performance': 'ALL'}
OPTIONS = Options()
# OPTIONS.add_argument("--headless")
driver = webdriver.Chrome(
                            executable_path='chromedriver',
                            desired_capabilities=CAPABILITIES,
                            options=OPTIONS
                        )
driver.maximize_window()

cookie = {'Cookie': login(args, driver)} # do Login.

driver.get(BASE_URL+"/webapps/gradebook/do/student/viewCourses")

try:
    WaitClickable(driver,(By.CLASS_NAME, "button-1")).click()
except:
    print("no tos warning - skipped")
SwitchToIFrame(driver, (By.ID, 'mybbCanvas'))

# get courseIDs
courses = driver.find_element_by_id("left_stream_mygrades")\
                .find_elements_by_xpath("//div[@role='tab']")

course_details = []
for i, course_results in enumerate(courses):
    course_results = courses[i]
    ActionChains(driver).move_to_element(course_results).perform()
    course_url = course_results.get_attribute("bb:rhs")
    course_name = course_results.find_elements_by_xpath("//span[@class='stream_area_name']")[i].text
    course_name += " ["+parse_qs(urlparse(course_url).query)['course_id'][0]+"]"
    course_details.append({
        'name': course_name,
        'url' : course_url
    })

path = ['grades']
for i, course in enumerate(course_details):
    path.append(course['name']) # course name
    print(course['name'])
    driver.get(BASE_URL+course['url'])

    driver.execute_script("""
    mygrades.loadContentFrame = function(url) {
        window.open(url);
    }
    """)

    WaitClickable(driver,(By.XPATH,"//a[@value='A']")).click()

    table = driver.find_elements_by_xpath("//div[@id='grades_wrapper']/div")

    save_html("/".join(path), path[0], driver.page_source)

    for i, assignment in enumerate(table):
        print(i)
        buttons = assignment.find_elements_by_tag_name("input")
        block = None
        assignment_name = None
        information_link = False
        try:
            block = assignment.find_element_by_xpath("./div[@class='cell gradable']/a[@onclick]")
            information_link = True
        except:
            block = assignment.find_element_by_xpath("./div[@class='cell gradable']")
        assignment_name = get_assignment_name(driver,block)
        path.append(assignment_name)
        # download information if it exists.
        if information_link:
            ActionChains(driver).move_to_element(block).click(block).perform()
            print("Switched "+assignment_name)
            WebDriverWait(driver,10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
            save_html("/".join(path),"information",driver.page_source)
            scrape_further(driver, "/".join(path))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        # download rubric if it exists.
        for button in buttons:
            action = button.get_attribute("onclick")
            if action != None and "showInLightBox" not in action:
                click_the_fing_button(driver,button)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                driver.switch_to.window(driver.window_handles[1])
                WaitDiv(driver, (By.CLASS_NAME, "rubricControlContainer"))
                save_html("/".join(path),"rubric",driver.page_source)
                driver.find_element_by_xpath("//li[@id='listViewTab']/a").click()
                WaitDiv(driver, (By.CLASS_NAME, "rubricGradingList"))
                save_html("/".join(path),"list",driver.page_source)
                detailed_buttons = driver.find_elements_by_xpath("//div[@class='u_controlsWrapper']/input")
                detailed_buttons[1].click()
                detailed_buttons[0].click()
                save_html("/".join(path),"list_detailed",driver.page_source)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        path.pop()
    WaitClickable(driver,(By.XPATH,"//a[@value='S']")).click()
    save_html("/".join(path),"submitted",driver.page_source)
    try:
        WaitClickable(driver,(By.XPATH,"//div[@id='submissionReceipts']//a")).click()
        WaitClickable(driver,(By.XPATH,"//div[@id='listContainer_itemcount']//a[@class='pagelink']")).click()
    except:
        print('No items?')
    save_html("/".join(path),"receipts",driver.page_source)
    path.pop()


driver.quit()