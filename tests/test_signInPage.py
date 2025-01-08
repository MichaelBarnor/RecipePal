from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import os
from webdriver_manager.chrome import ChromeDriverManager
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from unittest.mock import patch

# https://www.browserstack.com/guide/locators-in-selenium

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSignInTest(StaticLiveServerTestCase):
    port = 8000
    base_url = 'http://127.0.0.1:8000/'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # used/uncomment when testing locally
        # cls.selenium = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # used/comment when pushing to github
        chrome_options.binary_location = f"{os.environ['GITHUB_WORKSPACE']}/chrome/chrome-linux64/chrome"
        service = Service(f"{os.environ['GITHUB_WORKSPACE']}/chromedriver/chromedriver-linux64/chromedriver")
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)

        cls.selenium.implicitly_wait(10)

        site = Site.objects.get_current()
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )
        social_app.sites.add(site)

        patcher = patch('allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_app')
        cls.mock_get_app = patcher.start()
        cls.mock_get_app.return_value = social_app
        cls.addClassCleanup(patcher.stop)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_verify_signIn_contents(self):
        self.selenium.get(self.live_server_url)

        loginPage_buttons = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "btn-google"))
        )
        google_login_button = loginPage_buttons[0] 
        continue_without_login = loginPage_buttons[1]

        google_title = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/h1"))
        )                    
        
        footer = WebDriverWait(self.selenium, 10). until(
            EC.presence_of_element_located((By.TAG_NAME, 'footer'))
        )
        
        self.assertEqual(google_title.text.strip(), "RecipePal")
        self.assertEqual(google_login_button.text.strip(), "Login With Google")
        self.assertEqual(continue_without_login.text.strip(), 'Continue Without Logging In')
        self.assertEqual(footer.text.strip(), "This system is a class project. The system is not monitored, and no real information should be submitted.")
