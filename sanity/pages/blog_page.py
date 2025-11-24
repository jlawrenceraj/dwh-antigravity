from pages.base_page import BasePage

class BlogPage(BasePage):
    def __init__(self, driver, config):
        super().__init__(driver)
        self.config = config
        self.url = self.config['base_url'] + self.config['pages']['blog']['url']
        self.locators = self.config['pages']['blog']['locators']

    def load(self):
        self.driver.get(self.url)

    def verify_loaded(self):
        return "Blog" in self.get_title()
