#!/usr/bin/env python
import os,sys
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

current_path = str(os.getcwd())

psrlist_path = os.path.join(current_path,"tpa_psrs.list")
psrlist = np.genfromtxt(psrlist_path,dtype=str,comments="#",autostrip=True)

def get_url(psrname):
    url = "https://www.atnf.csiro.au/people/joh414/meerkat/{0}.html".format(psrname)
    return url

for psr in psrlist:
    print psr
    CHROME_PATH = '/usr/bin/google-chrome-stable'
    CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
    WINDOW_SIZE = "900,600"
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = CHROME_PATH
    driver = webdriver.Chrome(
            executable_path=CHROMEDRIVER_PATH,
            chrome_options=chrome_options
        )
    url = get_url(psr)
    driver.get(url)
    psrname = os.path.split(url)[-1].split(".html")[0]
    main_path = os.path.join(current_path,"webshots")
    if not os.path.exists(main_path):
        os.makedirs(main_path)
    save_path = os.path.join(current_path,"webshots/{0}.png".format(psrname))
    height = driver.execute_script("return document.body.scrollHeight")
    width = driver.execute_script("return document.body.scrollWidth")
    driver.set_window_size(width,height)
    driver.save_screenshot(save_path)
    driver.close()
    print "Screenshot taken for {0}".format(psr)
