from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.base_page import BasePage
import os
import datetime

def test_screenshot():
    # Setup driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Navigate to a page (e.g., google.com for simplicity, or just use blank)
        driver.get("https://www.google.com")
        
        # Initialize BasePage
        base_page = BasePage(driver)
        
        # Take screenshot
        screenshot_name = "test_screenshot"
        base_page.take_screenshot(screenshot_name)
        
        # Verify file existence
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        expected_path = os.path.join("screenshots", date_str, f"{screenshot_name}.png")
        
        if os.path.exists(expected_path):
            print(f"SUCCESS: Screenshot found at {expected_path}")
        else:
            print(f"FAILURE: Screenshot not found at {expected_path}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    test_screenshot()
