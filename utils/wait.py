from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
timeout = 5


def WaitClickable(driver, locator):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def WaitDiv(driver, locator):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def SwitchToIFrame(driver, locator):
    return WebDriverWait(driver, timeout).until(EC.frame_to_be_available_and_switch_to_it(locator))
