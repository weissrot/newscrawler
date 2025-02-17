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
from pprint import pformat
import urllib.request
from twocaptcha import TwoCaptcha
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from self_dump_page_source import *
import subprocess
class DumpPageSourceCommand(BaseCommand):
    def __init__(self, suffix):
        self.suffix = suffix

    def __repr__(self):
        return "DumpPageSourceCommand({})".format(self.suffix)

    def execute(
        self,
        webdriver,
        browser_params,
        manager_params,
        extension_socket,
    ):
        if self.suffix != "":
            self.suffix = self.suffix

        outname = md5(webdriver.current_url.encode("utf-8")).hexdigest()
        outfile = f"../html/{self.suffix}/{self.suffix}" + ".html"
        if not os.path.exists(f"../html/{self.suffix}/"):
            os.makedirs(f"../html/{self.suffix}/")

        with open(outfile, "wb") as f:
            f.write(webdriver.page_source.encode("utf8"))
            f.write(b"\n")

# driver = uc.Chrome(enable_cdp_events=True,version_main=126)

# Function to read URLs from websites.csv
     

# if len(sys.argv) > 1:
#     url = sys.argv[1]
#     print(url)
#     website_name = url.rsplit("//")[1].rsplit(".")[1]
#     driver.get(url)
#     time.sleep(20)

#         # Create a DumpPageSourceCommand instance with a suffix (if needed)
#     dump_command = DumpPageSourceCommand(suffix= website_name)

#         # Execute the command to save the page source
#     dump_command.execute(
#         webdriver=driver,
#         browser_params={},  # Replace with appropriate browser parameters
#         manager_params={
#             "source_dump_path": "../html/"
#         },  # Replace with the path where you want to save the source
#         extension_socket=None,  # Optional extension socket
#     )