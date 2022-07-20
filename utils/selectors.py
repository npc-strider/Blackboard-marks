from selenium.webdriver.common.by import By


class Selectors:
    # Microsoft login
    BOX_USERNAME = (By.ID, "i0116")
    BOX_PASSWORD = (By.ID, "i0118")
    DIV_USERERROR = (By.ID, 'usernameError')
    BUTTON_NEXT = (By.ID, "idSIButton9")
    BUTTON_DENY = (By.ID, "idBtn_Back")
    # Selectors for grades
