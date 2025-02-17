import csv
import requests
from selenium import webdriver
import base64
from hashlib import md5
import gzip
import json
import logging
import os
import random
import sys
import time
import traceback
from glob import glob
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pformat
import urllib.request
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import ElementNotInteractableException,ElementClickInterceptedException
from dump_page_source import DumpPageSourceCommand
driver = uc.Chrome(enable_cdp_events=True,version_main=133)
# Open the target webpage
#driver.get('https://openjur.de/suche/verkehr%20tod%20/0.ed-desc.html')
driver.get('https://de.ceair.com/newCMS/de/de/content/de_Footer/Support/201904/t20190403_5550.html')

# Find all links containing 'Beschluss' and '2025'
links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Kontakt')

# Save and modify the hrefs
hrefs = [link.get_attribute('href') for link in links]

# Visit each link one by one
for href in hrefs:
    count=0
    driver.get(href)
    time.sleep(2)
    latest_window_handle = driver.window_handles[-1]
    driver.switch_to.window(latest_window_handle)
    dump_command = DumpPageSourceCommand(suffix="jury")
    dump_command.execute(
        webdriver=driver,
        browser_params={},  # Replace with appropriate browser parameters
        manager_params={
            "source_dump_path": "./html/"
        },  # Replace with the path where you want to save the source
        extension_socket=None,  # Optional extension socket
    )
    count += 1

    break

input("Press Enter to close the browser...")
driver.quit()
