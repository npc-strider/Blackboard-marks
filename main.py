#!/usr/bin/env python3

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
# For chrome stuff
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
# ---
from urllib.parse import parse_qs, urlparse
import os
from os.path import sep
import re
import argparse

from utils.asset import RequestStack
from utils.wait import SwitchToIFrame, WaitClickable, WaitDiv
from constants.constants import BASE_URL, DL_DIR
from utils.login import login
from utils.utils import download_file, get_assignment_name, save_html
from pathlib import Path
from selenium.common.exceptions import ElementNotInteractableException

testing = False
try:
    testing = True
    from utils.test import get_etc  
except:
    def get_etc(*args): return False

# stupid bug
def click_the_fing_button(driver,button):
    try:
        ActionChains(driver).move_to_element(button)
        ActionChains(driver).click(button).perform()
        WebDriverWait(driver,2).until(EC.number_of_windows_to_be(2))
    except:
        driver.set_window_size(1024, 768)   # hack to wake selenium up when it doesnt want to click the button!
        click_the_fing_button(driver,button)
        driver.maximize_window()

# You can probably replace this with a recursive method like in blackboard scraper but tbh i just want to get this script done so i can stop working for once.
def scrape_further(driver,path,session):
    # attempts for bb-held tests
    attempts = driver.find_elements(By.XPATH, "//a[starts-with(@href, '/webapps/assessment')]")
    attempts = [ x.get_attribute('href') for x in attempts ]
    for i, attempt in enumerate(attempts):
        name = "attempt_"+str(i)+"_["+parse_qs(urlparse(attempt).query)['attempt_id'][0]+"]"
        attempt = re.sub("^"+BASE_URL,"",attempt)
        driver.execute_script("window.open('"+BASE_URL+attempt+"')")
        WebDriverWait(driver,10).until(EC.number_of_windows_to_be(3))
        driver.switch_to.window(driver.window_handles[2])
        save_html(path, name, driver.page_source)
        if testing:
            get_etc(driver, session, path)
        driver.close()
        driver.switch_to.window(driver.window_handles[1])

    # submission file for assignment
    request_stack = RequestStack(session)
    attempts = driver.find_elements(By.XPATH, "//a[starts-with(@href, '/webapps/assignment/download')]")
    attempts = [ x.get_attribute('href') for x in attempts ]
    for i, attempt in enumerate(attempts):
        request_stack.add_file(attempt,path)

    get_feedback = False
    try:
        # download button causes a tab to appear quickly, download, then disappear
        # need to capture the url to get the metadata and dl to the correct location
        # cant be arsed to figure out how the pspdfkit js that executes this download works.
        SwitchToIFrame(driver, (By.XPATH, "//iframe[@class='docviewer_iframe_embed']"))
        SwitchToIFrame(driver, (By.XPATH, "//iframe[@title='PSPDFKit']"))
        get_feedback = True
    except:
        print("No feedback to download")
    if get_feedback:
        dl_button = WaitClickable(driver,(By.XPATH, "//button[contains(@class,'PSPDFKit-Toolbar-Button PSPDFKit-Tool-Button')][@title='Download']"))
        dl_button.click()
        download_file(path)
    request_stack.download_all()
# end of scrape_further


parser = argparse.ArgumentParser(description='Automated microsoft SSO login.')
# parser.add_argument("-p", "--password", help="Automatically use provided password", default="")
parser.add_argument("-u", "--username", help="Automatically use provided userID", default="")

path = ['grades']
args = parser.parse_args()

CAPABILITIES = DesiredCapabilities.CHROME
CAPABILITIES['goog:loggingPrefs'] = {
    'performance'           : 'ALL',
}

for f in os.listdir(DL_DIR):
    os.remove(Path(DL_DIR).joinpath(f))
prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": DL_DIR,
            "directory_upgrade": True
        }
OPTIONS = Options()
OPTIONS.add_experimental_option("prefs", prefs)
# OPTIONS.add_argument("--headless")
driver = webdriver.Chrome(
                            executable_path='chromedriver.exe',
                            desired_capabilities=CAPABILITIES,
                            options=OPTIONS
                        )
driver.maximize_window()

cookies = login(args, driver) # do Login.
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie["name"], cookie["value"])

# need to load this page JUST to remove the tos warning so it doesnt fuck up everything down the line.
driver.get(BASE_URL+"/webapps/gradebook/do/student/viewCourses")
try:
    WaitClickable(driver,(By.CLASS_NAME, "button-1")).click()
except:
    print("no tos warning - skipped")

driver.get(BASE_URL+"/webapps/streamViewer/streamViewer?cmd=view&streamName=mygrades")
save_html(sep.join(path), 'entrypoint', driver.page_source)

# get courseIDs
courses = driver.find_element(By.ID, "left_stream_mygrades")\
                .find_elements(By.XPATH, "//div[@role='tab']")

course_details = []
for i, course_results in enumerate(courses):
    course_results = courses[i]
    ActionChains(driver).move_to_element(course_results).perform()
    course_url = course_results.get_attribute("bb:rhs")
    course_name = course_results.find_elements(By.XPATH, "//span[@class='stream_area_name']")[i].text
    course_name += " ["+parse_qs(urlparse(course_url).query)['course_id'][0]+"]"
    course_details.append({
        'name': course_name,
        'url' : course_url
    })

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
    WaitClickable(driver,(By.XPATH,"//a[@value='A']")).click()

    table = driver.find_elements(By.XPATH, "//div[@id='grades_wrapper']/div")

    for i, assignment in enumerate(table):
        print(i)
        buttons = assignment.find_elements(By.TAG_NAME, "input")
        block = None
        assignment_name = None
        information_link = False
        try:
            block = assignment.find_element(By.XPATH, "./div[@class='cell gradable']/a[@onclick]")
            information_link = True
        except:
            block = assignment.find_element(By.XPATH, "./div[@class='cell gradable']")
        assignment_name = get_assignment_name(driver,block)
        path.append(assignment_name)
        # download information if it exists.
        if information_link:
            try:
                ActionChains(driver).move_to_element(block).click(block).perform()
                print("Switched "+assignment_name)
                WebDriverWait(driver,10).until(EC.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])
                save_html(sep.join(path),"information",driver.page_source)
                scrape_further(driver, sep.join(path), session)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except ElementNotInteractableException:
                print('idk')
        # download rubric if it exists.
        for button in buttons:
            action = button.get_attribute("onclick")
            if action != None and "showInLightBox" not in action:
                click_the_fing_button(driver,button)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                driver.switch_to.window(driver.window_handles[1])
                WaitDiv(driver, (By.CLASS_NAME, "rubricControlContainer"))
                save_html(sep.join(path),"rubric",driver.page_source)
                driver.find_element(By.XPATH, "//li[@id='listViewTab']/a").click()
                WaitDiv(driver, (By.CLASS_NAME, "rubricGradingList"))
                save_html(sep.join(path),"list",driver.page_source)
                detailed_buttons = driver.find_elements(By.XPATH, "//div[@class='u_controlsWrapper']/input")
                detailed_buttons[1].click()
                detailed_buttons[0].click()
                save_html(sep.join(path),"list_detailed",driver.page_source)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        path.pop() 
    save_html(sep.join(path), path[0], driver.page_source)
    WaitClickable(driver,(By.XPATH,"//a[@value='S']")).click()
    save_html(sep.join(path),"submitted",driver.page_source)
    try:
        WaitClickable(driver,(By.XPATH,"//div[@id='submissionReceipts']//a")).click()
        WaitClickable(driver,(By.XPATH,"//div[@id='listContainer_itemcount']//a[@class='pagelink']")).click()
    except:
        print('No items?')
    save_html(sep.join(path),"receipts",driver.page_source)
    path.pop()


driver.quit()