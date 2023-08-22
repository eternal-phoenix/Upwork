import os
import load_django
import pickle
from categories import get_category
from parser_app import models
# from uploader_spreadsheets import spreadsheets_api_write_row
from config import LOGIN, PASSWORD

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains

from time import sleep
from datetime import timedelta
from django.utils import timezone
from tqdm import tqdm


PAGES_FOR_EACH_QUERY = 10  # <<<HERE IS PAGES NUMBER TO CHANGE IF NEEDED


class UpworkScraper():

    def __init__(self) -> None:

        self.DEBUG = False
        self.service = Service(ChromeDriverManager().install())
        self.chrome_options = Options()
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--enable-javascript')
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.maximize_window()
        self.actions = ActionChains(self.driver)


    def login(self):
        """simple login with inserting data into inputs, submitting and saving cookies to file"""
        print('\n[INFO] Performing login...\n')

        url = 'https://www.upwork.com/ab/account-security/login'
        login = LOGIN
        password = PASSWORD
        self.driver.get(url)
        sleep(1)
        login_input = self.driver.find_element(by=By.ID, value='login_username')
        login_input.clear()
        login_input.send_keys(login)
        login_input.send_keys(Keys.ENTER)
        sleep(1)
        login_input = self.driver.find_element(by=By.ID, value='login_password')
        login_input.clear()
        login_input.send_keys(password)
        login_input.send_keys(Keys.ENTER)
        sleep(5)

        # saving cookies
        with open('cookies.pkl', 'wb') as file:
            pickle.dump(self.driver.get_cookies(), file)


    def set_50_items_displayed(self):
        """set 50 elements on page presented instead of 10:
            find dropdown>click>click item in dropdown menu"""
        dropdown = self.driver.find_element(by=By.XPATH, value='//div[@class="up-dropdown jobs-per-page"]')
        self.actions.move_to_element(dropdown).click().perform()
        sleep(3)
        number = self.driver.find_elements(by=By.XPATH, value='.//span[@class="up-menu-item-text"]')[-1]
        self.actions.move_to_element(number).click().perform()
        sleep(5)
        

    def get_data(self, url: str) -> None:
        """process: 
            find all items on page;
            for each item find certain data sometimes with different item-search options for more capability;
        returns:
            the function returns different values while some errors/CloudFlare/success run;
            it is needed to perform different actions(rerun/sleep/go ahead) depend on returned result"""
        print(f'\n[INFO] getting data for url: {url}\n')

        # open and use previously saved cookies 
        with open('cookies.pkl', 'rb') as file:
            cookies = pickle.load(file)
        # apply cookies to the webdriver
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get(url)
        sleep(5)

        if 'Checking if the site connection is secure' in self.driver.page_source:
            print('\n[INFO] CloudFlare detected...\n')
            return 'CloudFlare'

        # performing increase displayed items amount if necessary
        if len(self.driver.find_elements(by=By.XPATH, value='//section[@data-test="JobTile"]')) == 10:
            try:
                self.set_50_items_displayed()
            except (NoSuchElementException, ElementNotInteractableException):
                print('\n[INFO] increase items failed...\n')
                return 'Element Not Interactable'
            
        items = self.driver.find_elements(by=By.XPATH, value='//section[@data-test="JobTile"]')
        for item in tqdm(items):
            try:
                offer_link_tag = item.find_element(by=By.XPATH, value='.//a[@data-test="UpLink"]')
                offer_link = offer_link_tag.get_attribute('href')
                offer_id = offer_link.split('_~')[1].replace('/', '')
                offer_name = offer_link_tag.text
                job_type = item.find_element(by=By.XPATH, value='.//strong[@data-test="job-type"]').text
                try:
                    tier = item.find_element(by=By.XPATH, value='.//span[@data-test="contractor-tier"]').text
                except NoSuchElementException:
                    try:
                        tier = item.find_element(by=By.XPATH, value='.//strong[@data-test="contractor-tier"]').text
                    except NoSuchElementException:
                        tier = None
                posted_on = item.find_element(by=By.XPATH, value='.//span[@data-test="UpCRelativeTime"]').text
                text = item.find_element(by=By.XPATH, value='.//span[@data-test="job-description-text"]').text
                salary, duration = None, None
            except StaleElementReferenceException:
                return 'Stale Element Reference'

            try:
                connects = item.find_element(By.XPATH, './/small[@data-test="connects-to-apply"]/strong').text
            except:
                connects = None

            if 'Hourly' in job_type:
                try:
                    job_type, salary = job_type.split(': ')
                except ValueError:
                    job_type = 'Hourly'
                try:
                    duration = item.find_element(by=By.XPATH, value='.//span[@data-test="duration"]').text
                except (NoSuchElementException, StaleElementReferenceException):
                    try:
                        duration = item.find_element(by=By.XPATH, value='.//strong[@data-test="workload"]').text
                    except (NoSuchElementException, StaleElementReferenceException):
                        duration = None

            elif 'Fixed-price' in job_type:
                try:
                    salary = item.find_element(by=By.XPATH, value='.//span[@data-test="budget"]').text
                except (NoSuchElementException, StaleElementReferenceException):
                    try:
                        salary = item.find_element(by=By.XPATH, value='.//strong[@data-test="budget"]').text
                    except (NoSuchElementException, StaleElementReferenceException):
                        salary = None

            # transform data to datetime format
            try:
                number = int(posted_on.split()[0])
            except ValueError:
                number = 1

            if 'sec' in posted_on:
                date_posted = timezone.now() - timedelta(seconds=number)
            elif 'min' in posted_on:
                date_posted = timezone.now() - timedelta(minutes=number)
            elif 'h' in posted_on:
                date_posted = timezone.now() - timedelta(hours=number)
            elif 'd' in posted_on:
                date_posted = timezone.now() - timedelta(days=number)
            else: 
                date_posted = None

            category = get_category(title=offer_name, text=text)
            
            if self.DEBUG:
                print('\n', offer_name, job_type, salary, tier, duration, date_posted, text, sep='\n')

            defaults = {
                'offer_link': offer_link, 
                'offer_name': offer_name, 
                'job_type': job_type,  
                'salary': salary, 
                'tier': tier,  
                'duration': duration,  
                'date_posted': date_posted,  
                'text': text,  
                'category': category, 
                'connects_to_apply': connects, 
            }
            obj, created = models.JobOfferInfo.objects.get_or_create(offer_id=offer_id, defaults=defaults)

        return 'Done'

    def self_destruction(self):
        self.driver.close()
        self.driver.quit()
 

def upload_to_disk():
    data_to_upload = [('Category', 'Offer name', 'Job type', 'Salary', 'Offer link', 'Offer id', 'Date posted'), ]
    for item in models.JobOfferInfo.objects.all():
        if item.date_posted:
            date = item.date_posted.strftime("%Y-%m-%d--%H:%M:%S")
        else:
            date = 'Too long ago'
        data = (
            item.category, 
            item.offer_name, 
            item.job_type, 
            item.salary, 
            item.offer_link, 
            item.offer_id, 
            date, 
        )
        data_to_upload.append(data)

    # spreadsheets_api_write_row(data_to_upload)
    print('\n[INFO] Data is written to google sheets...\n')
            

def bot_run():
    bot = UpworkScraper()
    bot.login()

    models.Page.objects.all().delete()
    for obj in models.SearchQuery.objects.filter(active=True):
        query = obj.name
        for i in range(1, PAGES_FOR_EACH_QUERY + 1):
            models.Page.objects.create(link=f'https://www.upwork.com/nx/jobs/search/?q={query}&sort=recency&page={i}')
    
    pages = models.Page.objects.filter(status=False)
    for page in pages:
        res = bot.get_data(page.link)
        while not res == 'Done':
            print(res)
            print('\n[INFO] retrying process...\n')
            if res == 'CloudFlare':
                sleep(45)
            res = bot.get_data(page.link)
    
        page.status = True
        page.save()

    bot.self_destruction()



if __name__ == '__main__':
    bot_run()
    upload_to_disk()














    # USE IF YOU ONLY NEED TO UPLOAD DATA TO GOOGLE SPREEDSHEETS
    # upload_to_disk()

    # WARNING: DELETE ALL DATA FROM DATABASE
    ###########################################
    # models.JobOfferInfo.objects.all().delete()
    # models.Page.objects.all().delete()













