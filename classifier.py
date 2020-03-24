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
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, PreText, Button, Toggle, OpenURL, TapTool, CheckboxButtonGroup
from bokeh.plotting import figure

import argparse
import shlex,glob

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image



parser = argparse.ArgumentParser(description="Interactive classifier for TPA pulsars")
parser.add_argument("-psrlist",dest="psrlist",help="Path to file with pulsar list.",required=True)
parser.add_argument("-tags", dest="taglist", help="Path to list of pre-defined tags", required=True)
args = parser.parse_args()


#Parsing input parameters
psrlist = np.genfromtxt(args.psrlist,dtype=str,comments="#",autostrip=True)
psrlist=psrlist.tolist()


source = ColumnDataSource(data=dict(rgba=[],))
#Setting up the main plots
psr_select = Select(title="Choose pulsar", value=psrlist[0], options=psrlist)
p = figure(plot_width = 1600, plot_height = 900)
p.image_rgba(image='rgba', x=0, y=0, dw=10, dh=10,source=source)
p.x_range.range_padding = p.y_range.range_padding = 0
p.xaxis.visible = None
p.yaxis.visible = None
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
status = PreText(text="",width=400)


def get_url(psrname):
    url = "https://www.atnf.csiro.au/people/joh414/meerkat/{0}.html".format(psrname)
    return url

def capture_screenshot(url):
    status.text = "Procuring a snapshot from the TPA webpage..."
    CHROME_PATH = '/usr/bin/google-chrome-stable'
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
    save_path = "/home/psr/TPA/TPA_Classifier/webshots/{0}.png".format(psrname)
    height = driver.execute_script("return document.body.scrollHeight")
    width = driver.execute_script("return document.body.scrollWidth")
    driver.set_window_size(width,height)
    driver.save_screenshot(save_path)
    status.text = "Webshot saved."
    driver.close()
    return save_path

def convert_image(save_path):
    if os.path.exists(save_path):
        print "sadad"
        status.text = "Converting image to RGBA vector."
        img = Image.open(save_path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        array = np.array(img)
    else:
        status.text = "Webshot not found."
        N = 20
        img = np.empty((N,N), dtype=np.uint32)
        array = img.view(dtype=np.uint8).reshape((N, N, 4))
        for i in range(N):
            for j in range(N):
                array[i, j, 0] = int(i/N*255)
                array[i, j, 1] = 158
                array[i, j, 2] = int(j/N*255)
                array[i, j, 3] = 255

    return array

def update():
    selected_psr = psr_select.value
    status.text = "Selected pulsar {0}".format(selected_psr)
    url = get_url(selected_psr)
    save_path = capture_screenshot(url)
    rgba_array = convert_image(save_path)
    status.text = "Success. Displaying plot below."
    source.data=dict(rgba=[rgba_array])


psr_select.on_change('value',lambda attr, old, new: update())

select_status = row(psr_select,status)
inputs_webshot = column(select_status,p)


l = layout([
    [inputs_webshot],
],sizing_mode='fixed')

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "TPA Classifier"
