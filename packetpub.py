import unittest
import smtplib
import traceback
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ConfigParser

def getConfig():
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'properties.ini'))
	return config

class TestMod2Selenium(unittest.TestCase):
    def setUp(self):
        config = getConfig()
        
        self.username = config.get('packetpub', 'USERNAME')
        self.password = config.get('packetpub', 'PASSWORD')
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1124, 850)  # set browser size.
        self.driver.delete_all_cookies

    def test_get_packetpub(self):
        driver = self.driver
        try:
            driver.get("https://www.packtpub.com/#")
            login = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id=\"account-bar-login-register\"]/a[1]/div"))
            )
            login.click()

            email = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//form[@id="packt-user-login-form"]//div[@id="email-wrapper"]/input[@id="email"]'))
            )
            email.send_keys(self.username + u'\ue004' + self.password + u'\ue007')

        except Exception, e:
            traceback.print_exc()

        driver.get("https://packtpub.com/packt/offers/free-learning")
        deal_of_the_day = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"deal-of-the-day\"]/div//input"))
        )
        deal_of_the_day.click()
        self.assertIn("https://www.packtpub.com/account/my-ebooks", self.driver.current_url)

    def tearDown(self):
        self.driver.close()

class TestResults(unittest.TestResult):
	@staticmethod
	def sendmail(msg):
		config = getConfig()
		s = smtplib.SMTP('localhost')
		s.sendmail(config.get('testresult','MAILFROM'), [config.get('testresult','MAILTO')], msg)
		s.quit()
		
	def addError(self, test, err):
		super(TestResults, self).addError(test, err)
		error = self._exc_info_to_string(err, test)
		TestResults.sendmail('Subject: {}\n\n{}'.format('Packetpub Error', error))
		
	def addFailure(self, test, err):
		super(TestResults, self).addFailure(test, err)
		error = self._exc_info_to_string(err, test)
		TestResults.sendmail('Subject: {}\n\n{}'.format('Packetpub Error', error))
        


if __name__ == '__main__':
	suite = unittest.TestSuite(
        unittest.TestLoader().discover(os.path.join(os.path.abspath(os.path.dirname(__file__))), "packetpub.py")
    )
	results = TestResults()
	suite.run(results)
