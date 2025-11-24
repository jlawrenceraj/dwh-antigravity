import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.blog_page import BlogPage
from pages.contact_page import ContactPage
from selenium.webdriver.chrome.options import Options
from utils.email_sender import send_email_with_screenshots
import os
import datetime

def load_config(config_path="config.yaml"):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    config = load_config()
    
    # Setup WebDriver
    chrome_options = Options()
    if config.get('headless', False):
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080") # Important for headless to render correctly

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    if not config.get('headless', False):
        driver.maximize_window()

    # Create screenshots directory
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    captured_screenshots = []

    try:
        print("Starting Sanity Check...")
        results = []

        # 1. Login
        print("1. Testing Login Page...")
        login_page = LoginPage(driver, config)
        login_page.load()
        login_page.login(config['credentials']['username'], config['credentials']['password'])
        
        screenshot_path = os.path.join(screenshots_dir, f"login_success_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        captured_screenshots.append(screenshot_path)

        if login_page.verify_login_success():
            print("   [PASS] Login Successful")
            results.append("Login: PASS")
        else:
            print("   [FAIL] Login Failed")
            results.append("Login: FAIL")
            return # Stop if login fails

        # 2. Home Page
        print("2. Testing Home Page...")
        home_page = HomePage(driver, config)
        home_page.load()
        
        screenshot_path = os.path.join(screenshots_dir, f"home_page_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        captured_screenshots.append(screenshot_path)

        if home_page.verify_loaded():
             print("   [PASS] Home Page Loaded")
             results.append("Home Page: PASS")
        else:
             print("   [FAIL] Home Page Not Loaded")
             results.append("Home Page: FAIL")

        # 3. Blog Page
        print("3. Testing Blog Page...")
        blog_page = BlogPage(driver, config)
        blog_page.load()
        
        screenshot_path = os.path.join(screenshots_dir, f"blog_page_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        captured_screenshots.append(screenshot_path)

        if blog_page.verify_loaded():
             print("   [PASS] Blog Page Loaded")
             results.append("Blog Page: PASS")
        else:
             print("   [FAIL] Blog Page Not Loaded")
             results.append("Blog Page: FAIL")

        # 4. Contact Page
        print("4. Testing Contact Page...")
        contact_page = ContactPage(driver, config)
        contact_page.load()
        
        screenshot_path = os.path.join(screenshots_dir, f"contact_page_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        captured_screenshots.append(screenshot_path)

        if contact_page.verify_loaded():
             print("   [PASS] Contact Page Loaded")
             results.append("Contact Page: PASS")
        else:
             print("   [FAIL] Contact Page Not Loaded")
             results.append("Contact Page: FAIL")

        print("Sanity Check Completed.")
        
        # Send Email
        if config.get('email'):
            print("Sending email report...")
            subject = f"Sanity Check Report - {timestamp}"
            body = "Sanity Check Results:\n" + "\n".join(results)
            send_email_with_screenshots(subject, body, captured_screenshots, config)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
