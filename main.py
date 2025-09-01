from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import json
from webdriver_manager.chrome import ChromeDriverManager


class EasyApplyLinkedin:
    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']

        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # optional

        # ✅ webdriver-manager handles driver download
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
    def login_linkedin(self):
        """This function logs into your personal LinkedIn profile"""

        self.driver.get("https://www.linkedin.com/login")

        login_email = self.driver.find_element(By.NAME, 'session_key')
        login_email.clear()
        login_email.send_keys(self.email)

        login_pass = self.driver.find_element(By.NAME, 'session_password')
        login_pass.clear()
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.RETURN)

    def job_search(self):
        """Go to Jobs section and search for keywords and location"""

        jobs_link = self.driver.find_element(By.LINK_TEXT, 'Jobs')
        jobs_link.click()

        search_keywords = self.driver.find_element(By.CSS_SELECTOR, ".jobs-search-box__text-input[aria-label='Search jobs']")
        search_keywords.clear()
        search_keywords.send_keys(self.keywords)

        search_location = self.driver.find_element(By.CSS_SELECTOR, ".jobs-search-box__text-input[aria-label='Search location']")
        search_location.clear()
        search_location.send_keys(self.location)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        """Filter job results by 'Easy Apply'"""

        all_filters_button = self.driver.find_element(By.XPATH, "//button[@data-control-name='all_filters']")
        all_filters_button.click()
        time.sleep(1)

        easy_apply_button = self.driver.find_element(By.XPATH, "//label[@for='f_LF-f_AL']")
        easy_apply_button.click()
        time.sleep(1)

        apply_filter_button = self.driver.find_element(By.XPATH, "//button[@data-control-name='all_filters_apply']")
        apply_filter_button.click()

    def find_offers(self):
        """Find all job offers and apply"""

        total_results = self.driver.find_element(By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
        print(total_results_int)

        time.sleep(2)
        current_page = self.driver.current_url
        results = self.driver.find_elements(By.CLASS_NAME, "occludable-update.artdeco-list__item--offset-4.artdeco-list__item.p0.ember-view")

        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements(By.CLASS_NAME, 'job-card-search__title.artdeco-entity-lockup__title.ember-view')
            for title in titles:
                self.submit_apply(title)

        if total_results_int > 24:
            time.sleep(2)
            find_pages = self.driver.find_elements(By.CLASS_NAME, "artdeco-pagination__indicator.artdeco-pagination__indicator--number")
            total_pages = find_pages[len(find_pages) - 1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {total_pages_int}']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)

            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=', 1)[1])

            for page_number in range(25, total_jobs + 25, 25):
                self.driver.get(current_page + '&start=' + str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements(By.CLASS_NAME, "occludable-update.artdeco-list__item--offset-4.artdeco-list__item.p0.ember-view")
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements(By.CLASS_NAME, 'job-card-search__title.artdeco-entity-lockup__title.ember-view')
                    for title_ext in titles_ext:
                        self.submit_apply(title_ext)
        else:
            self.close_session()

    def submit_apply(self, job_add):
        """Submit application for a job"""

        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)

        try:
            in_apply = self.driver.find_element(By.XPATH, "//button[@data-control-name='jobdetails_topcard_inapply']")
            in_apply.click()
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            return
        time.sleep(1)

        try:
            submit = self.driver.find_element(By.XPATH, "//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
        except NoSuchElementException:
            print('Not direct application, going to next...')
            try:
                discard = self.driver.find_element(By.XPATH, "//button[@data-test-modal-close-btn]")
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = self.driver.find_element(By.XPATH, "//button[@data-test-dialog-primary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass

        time.sleep(1)

    def close_session(self):
        """Close browser session"""
        print('End of the session, see you later!')
        self.driver.quit()

    def apply(self):
        """Run the bot"""
        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(2)
        self.find_offers()
        time.sleep(2)
        self.close_session()


if __name__ == '__main__':
    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()
