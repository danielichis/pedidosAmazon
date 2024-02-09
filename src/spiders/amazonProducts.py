from playwright.sync_api import sync_playwright
from src.utils.readconfig import settingsData as stt

class Amazon:
    def __init__(self) -> None:
        self.p= sync_playwright().start()
        self.browser = self.p.chromium.launch_persistent_context(user_data_dir=stt.user_data_dir,headless=True)
        self.page = self.browser.new_page()
    
    def scrape_product(self):
        response = self.page.goto("https://www.amazon.com/dp/B08ZJQVV6G")
        print(response.status)

if __name__ == "__main__":
    amazon = Amazon()
    amazon.scrape_product()