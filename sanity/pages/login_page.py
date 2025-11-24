from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver, config):
        super().__init__(driver)
        self.config = config
        self.url = self.config['base_url'] + self.config['pages']['login']['url']
        self.locators = self.config['pages']['login']['locators']

    def load(self):
        self.driver.get(self.url)

    def login(self, username, password):
        self.enter_text(self.locators['username_input'], username)
        self.enter_text(self.locators['password_input'], password)
        self.click(self.locators['submit_button'])

    def verify_login_success(self):
        return self.is_displayed(self.locators['success_message'])
