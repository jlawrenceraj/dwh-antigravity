from pages.base_page import BasePage

class ContactPage(BasePage):
    def __init__(self, driver, config):
        super().__init__(driver)
        self.config = config
        self.url = self.config['base_url'] + self.config['pages']['contact']['url']
        self.locators = self.config['pages']['contact']['locators']

    def load(self):
        self.driver.get(self.url)

    def verify_loaded(self):
        return self.is_displayed(self.locators['header'])
