from pages.base_page import BasePage

class HomePage(BasePage):
    def __init__(self, driver, config):
        super().__init__(driver)
        self.config = config
        # Note: The home page URL might be different after login, but for direct navigation:
        self.url = self.config['base_url'] + self.config['pages']['home']['url']
        self.locators = self.config['pages']['home']['locators']

    def load(self):
        self.driver.get(self.url)

    def verify_loaded(self):
        # Check for a specific element that confirms we are on the home page
        # For example, a header or a specific menu item
        return self.is_displayed(self.locators['header'])
