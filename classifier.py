#!/usr/bin/env python

"""
TPA Classifier: Interactive classifier for TPA pulsars.

__author__ = "Aditya Parthasarathy"
__copyright__ = "Copyright 2020,TPA"
__license__ = "Public Domain"
__version__ = "0.1"
__maintainer__ = "Aditya Parthasarathy"
__email__ = "adityapartha3112@gmail.com"
__status__ = "Development"

"""

import os,sys
import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, layout, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, PreText, Button, Toggle, OpenURL, TapTool
from bokeh.plotting import figure

import argparse
import shlex,glob

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


parser = argparse.ArgumentParser(description="Interactive classifier for TPA pulsars")
parser.add_argument("-psrlist",dest="psrlist",help="Path to file with pulsar list.",required=True)
parser.add_argument("-tags", dest="taglist", help="Path to list of pre-defined tags", required=True)
args = parser.parse_args()

def get_url(psrname):
    url = "https://www.atnf.csiro.au/people/joh414/meerkat/{0}.html".format(psrname)
    return url

def capture_screenshot(url):
    CHROME_PATH = '/usr/bin/google-chrome'
    CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
    WINDOW_SIZE = "700,300"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = CHROME_PATH
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH,
        chrome_options=chrome_options
    )
    driver.get(url)
    psrname = os.path.split(url)[-1].split(".html")[0]
    save_path = "webshots/{0}.png".format(psrname)
    driver.save_screenshot(save_path)
    driver.close()
    return save_path

def update():
    selected_psr = psrs_select.value
    url = get_url(selected_psr)
    save_path = capture_screenshot(url)


l = layout([
    [plot_update,sliders_texts,USER_TEXT],
],sizing_mode='fixed')

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "TPA Classifier"
