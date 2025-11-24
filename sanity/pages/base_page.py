from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import datetime

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    def _parse_locator(self, locator_str):
        """Parses a locator string like 'id:username' into (By.ID, 'username')"""
        if ":" not in locator_str:
            raise ValueError(f"Invalid locator format: {locator_str}. Expected 'type:value'")
        
        by_type, value = locator_str.split(":", 1)
        by_type = by_type.lower()
        
        if by_type == "id":
            return (By.ID, value)
        elif by_type == "name":
            return (By.NAME, value)
        elif by_type == "xpath":
            return (By.XPATH, value)
        elif by_type == "css":
            return (By.CSS_SELECTOR, value)
        elif by_type == "class":
            return (By.CLASS_NAME, value)
        else:
            raise ValueError(f"Unsupported locator type: {by_type}")

    def find_element(self, locator_str):
        locator = self._parse_locator(locator_str)
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            print(f"Element not found: {locator_str}")
            return None

    def click(self, locator_str):
        element = self.find_element(locator_str)
        if element:
            element.click()
        else:
            raise Exception(f"Could not click element: {locator_str}")

    def enter_text(self, locator_str, text):
        element = self.find_element(locator_str)
        if element:
            element.clear()
            element.send_keys(text)
        else:
            raise Exception(f"Could not enter text into element: {locator_str}")

    def get_text(self, locator_str):
        element = self.find_element(locator_str)
        if element:
            return element.text
        return None

    def is_displayed(self, locator_str):
        element = self.find_element(locator_str)
        return element.is_displayed() if element else False

    def get_title(self):
        return self.driver.title

    def take_screenshot(self, name):
        """
        Takes a screenshot and saves it to a folder named with the current date.
        Overwrites if file exists.
        """
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        directory = os.path.join("screenshots", date_str)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        file_path = os.path.join(directory, f"{name}.png")
        self.driver.save_screenshot(file_path)
        print(f"Screenshot saved to {file_path}")
