from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# find_element_safe = lambda name,timeout=30:WebDriverWait(driver, timeout).until(lambda x: x.find_element_by_id(name))
WaitClickable = lambda driver,locator:WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))
WaitDiv = lambda driver,locator:WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
SwitchToIFrame = lambda driver,locator:WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it(locator))