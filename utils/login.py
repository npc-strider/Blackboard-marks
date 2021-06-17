from utils.wait import WaitClickable
from utils.selectors import Selectors
import sys
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlparse
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass
from constants.constants import BASE_URL
import re
import json

def try_cookie(driver):
    for entry in driver.get_log('performance'):
        parameters = json.loads(entry["message"])['message']['params']
        if (
            'documentURL' in  parameters.keys()
            and re.search(r'https://lms.uwa.edu.au/webapps/portal.*', parameters['documentURL']) != None
        ):
            return parameters['redirectResponse']['requestHeaders']['Cookie']

def login(args, driver):
    USERNAME = args.username
    if len(USERNAME) == 0:
        print('UserID: ')
        USERNAME = input()
    USERNAME += '@student.uwa.edu.au'
    print('Password: ')
    PASSWORD = getpass('')
    
    driver.get(BASE_URL)

    WaitClickable(driver,Selectors.BOX_USERNAME).send_keys(USERNAME)
    WaitClickable(driver,Selectors.BUTTON_NEXT).click()
    print('Entered username.')

    try:
        WaitClickable(driver,Selectors.BOX_PASSWORD).send_keys(PASSWORD)
        WaitClickable(driver,Selectors.BUTTON_NEXT).click()
        print('Entered password.')
    except:
        print(WebDriverWait(driver, 1).until(EC.visibility_of_element_located(Selectors.DIV_USERERROR)).text)
        driver.quit()
        exit(2)

    WaitClickable(driver,Selectors.BUTTON_DENY).click()
    # WaitClickable(driver,BUTTON_NEXT).click() #IF you want to remember credentials, switch these comments
    current_uri = urlparse(driver.current_url)
    if '{uri.scheme}://{uri.netloc}'.format(uri=current_uri) != BASE_URL:
        driver.quit()
        print("Login failed.")
        exit(-1)
    
    return try_cookie(driver)