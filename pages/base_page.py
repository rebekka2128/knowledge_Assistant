from config import WEB_BASE_URL

class BasePage:
    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(WEB_BASE_URL)
        return self