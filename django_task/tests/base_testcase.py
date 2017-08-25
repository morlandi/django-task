import os
import django
import time
import webbrowser
# from selenium_utility_belt import SeleniumUtilityBelt
# from selenium import webdriver
# from django.test import LiveServerTestCase
#from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from tempfile import NamedTemporaryFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError

FIXTURES_DIR = os.path.join(settings.BASE_DIR, 'tasks/tests/fixtures')
#FIXTURES_LIST = [os.path.join(FIXTURES_DIR, 'workflows.json'), ]
FIXTURES_LIST = []


class BaseTestCase(django.test.TransactionTestCase):

    fixtures = FIXTURES_LIST

    def setUp(self):
        self.admin_username = 'admin'
        self.admin_password = 'password'
        User = get_user_model()
        self.admin = User.objects.create_superuser(self.admin_username, self.admin_username+'@noreply.com', self.admin_password)
        print ''
        print '-' * 80
        super(BaseTestCase, self).setUp()
        self.populate()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

    def view_html_page(self, content):
        f = NamedTemporaryFile('w')
        f.write(unicode(content).encode('utf-8'))
        f.flush()
        webbrowser.open('file://'+f.name)
        time.sleep(1)
        f.close()

    def populate(self):
        pass

    def isResponseOK(self, response):
        return response.status_code >= 200 and response.status_code < 300

    def assertResponseOK(self, response):
        self.assertTrue(self.isResponseOK(response))

    def assertResponseKO(self, response):
        self.assertFalse(self.isResponseOK(response))


# class BaseTestCaseForClient(BaseTestCase):

#     def setUp(self):
#         self.client = Client()
#         super(BaseTestCaseForClient, self).setUp()

#     def tearDown(self):
#         super(BaseTestCaseForClient, self).tearDown()

#     def login(self):
#         logged_in = self.client.login(username=self.admin_username, password=self.admin_password)
#         self.assertTrue(logged_in)


# class BaseTestCaseForSelenium(BaseTestCase, SeleniumUtilityBelt, StaticLiveServerTestCase):

#     def setUp(self):
#         super(BaseTestCaseForSelenium, self).setUp()

#     def tearDown(self):
#         # Call tearDown to close the web browser
#         # If this doesn't work, manually kill phantomjs processes as follows:
#         #   $ pgrep phantomjs | xargs kill
#         self.driver.quit()
#         super(BaseTestCaseForSelenium, self).tearDown()

#     def login(self):
#         # Open the login page
#         self.open("/login/")
#         # Fill login information of admin
#         username = self.get_elements_or_raise("#id_username")[0]
#         username.send_keys(self.admin_username)
#         password = self.get_elements_or_raise("#id_password")[0]
#         password.send_keys(self.admin_password)
#         # Locate form button and click it
#         #self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
#         self.driver.find_element_by_xpath('//form/button').click()

