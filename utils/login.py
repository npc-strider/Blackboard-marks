import sys
from utils.wait import WaitClickable
from utils.selectors import Selectors
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlparse
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass
from constants.constants import BASE_URL
import re
import json


def login(args, driver):
    driver.get(BASE_URL)
    USERNAME = args.username
    if len(USERNAME) == 0:
        print('UserID: ')
        USERNAME = input()
    USERNAME += '@student.uwa.edu.au'
    print('Password: ')
    PASSWORD = getpass('')

    WaitClickable(driver, Selectors.BOX_USERNAME).send_keys(USERNAME)
    WaitClickable(driver, Selectors.BUTTON_NEXT).click()
    print('Entered username.')

    try:
        WaitClickable(driver, Selectors.BOX_PASSWORD).send_keys(PASSWORD)
        WaitClickable(driver, Selectors.BUTTON_NEXT).click()
        print('Entered password.')
    except Exception:
        print(WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located(Selectors.DIV_USERERROR)).text)
        driver.quit()
        exit(2)

    WaitClickable(driver, Selectors.BUTTON_DENY).click()
    # WaitClickable(driver,BUTTON_NEXT).click() #IF you want to remember credentials, switch these comments

    cookie = driver.get_cookies()
    if cookie is not None:
        return cookie

    print('Could not get auth cookie - Invalid ID or password?', file=sys.stderr)
    driver.quit()
    exit(1)
