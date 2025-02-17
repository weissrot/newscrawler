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
# when use time: ed-desc
for page in range(3):
    driver.get(f'https://openjur.de/suche/verkehr%20tod/{page}.wh-desc.html')

    links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'vom')
    hrefs = [link.get_attribute('href') for link in links if any(year in link.text for year in ["2025", "2024","2023","2022","2021","2020","2019"])]

    count = 0
    for href in hrefs:
        driver.get(href)
        time.sleep(2)
        latest_window_handle = driver.window_handles[-1]
        driver.switch_to.window(latest_window_handle)
        dump_command = DumpPageSourceCommand(suffix= f"jury_{count}")
        dump_command.execute(
            webdriver=driver,
            browser_params={},  
            manager_params={
                "source_dump_path": "./html/"
            },  
            extension_socket=None, 
        )
        count += 1
        time.sleep(2)

input("Press Enter to close the browser...")
driver.quit()
