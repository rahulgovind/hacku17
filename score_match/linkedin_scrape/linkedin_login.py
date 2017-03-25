from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

def web_driver(email = 'anmol1696@gmail.com', password = 'qwertyuiop[]'):
    baseurl = 'https://www.linkedin.com/uas/login'
    driver = webdriver.Firefox()
    
    driver.get(baseurl)

    xpaths = {
        'email' : "//input[@name = 'session_key']",
        'password' : "//input[@name = 'session_password']",
        'login' : "//input[@name = 'signin']",
    }

    try:
        driver.find_element_by_xpath(xpaths['email']).send_keys(email)
        driver.find_element_by_xpath(xpaths['password']).send_keys(password)
        driver.find_element_by_xpath(xpaths['login']).click()
        time.sleep(5)
    except:
        return 0

    return driver

if __name__ == "__main__":
    web_driver()
