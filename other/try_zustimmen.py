from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
zustimmen_keywords = ["zustimmen", "ich bin einverstanden"]
driver = webdriver.Chrome() 
url = "https://muenchen.t-online.de/region/muenchen/id_100570082/muenchen-mann-stuerzt-sechs-meter-in-die-tiefe-schwer-verletzt.html"
driver.get(url)
time.sleep(3)
driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Iframe title']"))
buttons = driver.find_elements(By.TAG_NAME, "button")
time.sleep(1)
try:
    for button in buttons:
        print(button.get_attribute('title'))
        if any(keyword in button.get_attribute("innerHTML").lower() for keyword in zustimmen_keywords):
            driver.execute_script("arguments[0].click();", button)
            button.click()
except Exception:
    pass
input('print sth to quit')
            
driver.quit()
