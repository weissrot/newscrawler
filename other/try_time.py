from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
driver = webdriver.Chrome() 
url = "https://www.sueddeutsche.de/panorama/arbeitsunfall-mann-stuerzt-von-geruest-und-stirbt-dpa.urn-newsml-dpa-com-20090101-241016-930-262086"
driver.get(url)
time.sleep(3)
date = driver.find_element(By.XPATH, "//time[@data-manual='date']").get_attribute("datetime").split()[0]  
print(date)

input('print sth to quit')
            
driver.quit()