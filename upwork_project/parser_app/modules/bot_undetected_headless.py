from categories import get_category
import os
import load_django
import pickle
from parser_app import models
from uploader_spreadsheets import spreadsheets_api_write_row
from config import LOGIN, PASSWORD

from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys

from time import sleep
from datetime import timedelta
from django.utils import timezone
from pprint import pprint
from tqdm import tqdm
from selenium.webdriver.common.action_chains import ActionChains


PAGES_FOR_EACH_QUERY = 50  # <<<HERE IS PAGES NUMBER TO CHANGE IF NEEDED


class UpworkScraper():

    def __init__(self) -> None:

        self.DEBUG = False
        self.chrome_options = ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--enable-javascript')
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.actions = ActionChains(self.driver)


    def login(self):

        print('\n[INFO] performing login...\n')

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

        # save cookies
        with open('cookies.pkl', 'wb') as file:
            pickle.dump(self.driver.get_cookies(), file)

    def get_data(self, url: str) -> None:

        print(f'\n[INFO] getting data for url: {url}\n')

        with open('cookies.pkl', 'rb') as file:
            cookies = pickle.load(file)
        # add cookies to the webdriver
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get(url)
        sleep(2)
        if 'Checking if the site connection is secure' in self.driver.page_source:
            print('\n[INFO] CloudFlare detected...\n')
            return 'CloudFlare'

        items = self.driver.find_elements(by=By.XPATH, value='//section[@data-test="JobTile"]')
        for item in tqdm(items):
            try:
                offer_link_tag = item.find_element(by=By.XPATH, value='.//a[@data-test="UpLink"]')
                offer_link = offer_link_tag.get_attribute('href')
                offer_id = offer_link.split('_~')[1].replace('/', '')
                offer_name = offer_link_tag.text
                job_type = item.find_element(by=By.XPATH, value='.//strong[@data-test="job-type"]').text
                tier = item.find_element(by=By.XPATH, value='.//strong[@data-test="contractor-tier"]').text
                posted_on = item.find_element(by=By.XPATH, value='.//span[@data-test="UpCRelativeTime"]').text
                text = item.find_element(by=By.XPATH, value='.//span[@data-test="job-description-text"]').text
                salary, duration = None, None
            except StaleElementReferenceException:
                return 'Error'
            
            try:
                connects = item.find_element(By.XPATH, './/small[@data-test="connects-to-apply"]/strong').text
            except:
                connects = None
                
            print(f'\n[INFO] connects - {connects}\n')
            if 'Hourly' in job_type:
                try:
                    job_type, salary = job_type.split(': ')
                except ValueError:
                    job_type = 'Hourly'
                try:
                    duration = item.find_element(by=By.XPATH, value='.//strong[@data-test="workload"]').text
                except (NoSuchElementException, StaleElementReferenceException):
                    duration = None
            elif 'Fixed-price' in job_type:
                try:
                    salary = item.find_element(by=By.XPATH, value='.//span[@data-itemprop="baseSalary"]').text
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
            # connects_to_apply = item.find_element(by=By.XPATH, value='.//strong[@data-test="connect-price"]').text
            
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
            

def bot_run_page(page):

    bot = UpworkScraper()
    bot.login()

    res = bot.get_data(page.link)
    while not res == 'Done':
        print('\n[INFO] retrying process...\n')
        print(res)
        if res == 'CloudFlare':
            sleep(45)
        res = bot.get_data(page.link)

    bot.self_destruction()
    page.status = True
    page.save()


def upload_to_disk():
    data_to_upload = [('Category', 'Offer name', 'Job type', 'Salary', 'Offer link', 'Offer id', 'Date posted'), ]
    for item in models.JobOfferInfo.objects.all():
        if date:
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

    spreadsheets_api_write_row(data_to_upload)
 

def main():

    models.Page.objects.all().delete()
    for obj in models.SearchQuery.objects.filter(active=True):
        query = obj.name
        for i in range(1, PAGES_FOR_EACH_QUERY + 1):
            models.Page.objects.create(link=f'https://www.upwork.com/nx/jobs/search/?q={query}&sort=recency&page={i}')
    
    pages = models.Page.objects.filter(status=False)
    for page in pages:
        bot_run_page(page)

    upload_to_disk()


if __name__ == '__main__':
    main()












    # WARNING: DELETE ALL DATA FROM DATABASE
    ###########################################
    # models.JobOfferInfo.objects.all().delete()











