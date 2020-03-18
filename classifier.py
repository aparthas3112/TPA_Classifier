#!/usr/bin/env python

"""
TPA Classifier: P-Pdot based interactive classifier.

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


parser = argparse.ArgumentParser(description="Interactive classifier for TPA pulsars")
parser.add_argument("-load",dest="load_pickle",help="Path to the Gsheet pickle file.",required=True)
parser.add_argument("-psrcat", dest="psrcat", help="Path to the full catalogue pickle file", required=True)
args = parser.parse_args()

df = pd.read_pickle(str(args.load_pickle))
df_cat = pd.read_pickle(str(args.psrcat))
df_cat["color"] = "#7f8c8d"
df_cat["alpha"] = 0.6
df_cat["size"] = 7


#Set color and alpha
df["color"] = np.where(df["DM"] > 0, "#3498db", "grey")
df["alpha"] = np.where(df["DM"] > 0, 0.9, 0.25)
df['size'] = np.where(df["DM"] > 0, 9, 5)

#Replacing empty,NAN cells
df["ASSOC"].fillna("NA",inplace=True)
df["BNAME"].replace("","NA",inplace=True)
df["CATEGORY"].replace(np.nan,"UC",inplace=True)
df["COMMENTS"].replace(np.nan,"NA",inplace=True)

#Converting columns to appropriate data types
df["DM"] = pd.to_numeric(df["DM"], downcast="float")
df["RM"] = pd.to_numeric(df["RM"], downcast="float")
df["F0"] = pd.to_numeric(df["F0"], downcast="float")
df["F1"] = pd.to_numeric(df["F1"], downcast="float")
df["P0"] = pd.to_numeric(df["P0"], downcast="float")
df["P1"] = pd.to_numeric(df["P1"], downcast="float")
df["DIST"] = pd.to_numeric(df["DIST"], downcast="float")
df["PB"] = pd.to_numeric(df["PB"], downcast="float")
df["AGE"] = pd.to_numeric(df["AGE"], downcast="float")
df["BSURF"] = pd.to_numeric(df["BSURF"], downcast="float")
df["EDOT"] = pd.to_numeric(df["EDOT"], downcast="float")
df["NGLT"] = pd.to_numeric(df["NGLT"], downcast="integer")
df["rm_MK"] = pd.to_numeric(df["rm_MK"], downcast="float")
df["dm_MK"] = pd.to_numeric(df["dm_MK"], downcast="float")
df["w50_MK"] = pd.to_numeric(df["w50_MK"], downcast="float")
df["w10_MK"] = pd.to_numeric(df["w10_MK"], downcast="float")

#Normalising relevant columns
df["F1"] = df["F1"]/10**-13
df["AGE"] = df["AGE"]/10**3
df["BSURF"] = df["BSURF"]/10**10
df["EDOT"] = df["EDOT"]/10**30

df["F1"] = np.log10(abs(df["F1"]).astype("float64"))
df["AGE"] = np.log10(df["AGE"].astype("float64"))
df["BSURF"] = np.log10(df["BSURF"].astype("float64"))
df["EDOT"] = np.log10(df["EDOT"].astype("float64"))

# Create Input controls
F0 = Slider(title="Spin-frequency(F0)", value=df["F0"].min(), start=df["F0"].min(), end=df["F0"].max(), step=1)
F1 = Slider(title="Spin-frequency derivative(F1)(log)", value=df["F1"].min(), start=df["F1"].min(), end=df["F1"].max(), step=0.5)
DM = Slider(title="Dispersion measure(DM)", value=df["DM"].min(), start=df["DM"].min(), end=df["DM"].max(), step=0.5)
RM = Slider(title="Rotation measure(RM)", value=df["RM"].min(), start=df["RM"].min(), end=df["RM"].max(), step=0.5)
DIST = Slider(title="Distance", value=df["DIST"].min(), start=df["DIST"].min(), end=df["DIST"].max(), step=0.5)
AGE = Slider(title="Characteristic age(log)", value=df["AGE"].min(), start=df["AGE"].min(), end=df["AGE"].max(), step=0.5)
BSURF = Slider(title="Surface B-field(BSURF)(log)", value=df["BSURF"].min(), start=df["BSURF"].min(), end=df["BSURF"].max(), step=0.5)
EDOT = Slider(title="Energy loss(EDOT)(log)", value=df["EDOT"].min(), start=df["EDOT"].min(), end=df["EDOT"].max(), step=0.5)

ASSOC = Select(title="Association", options=df["ASSOC"].unique().tolist(), value="NA")

F1_TEXT = PreText(text='', width=500)
AGE_TEXT = PreText(text='', width=500)
BSURF_TEXT = PreText(text='', width=500)
EDOT_TEXT = PreText(text='', width=500)
USER_TEXT = PreText(text="""TODO:
1. Make P-Pdot plot more useful.
2. Add user comments.
3. Add classification tags to all the TPA pulsars.
4. Add URLs to Simon's webpage.
5. Feedback.
""", width=500)

CATALOGUE = Toggle(label="Toggle catalogue", width=300, button_type="success")
UPDATE = Button(label="Update",width=300)

profile_map = {
    "Gaussian": "GAU",
    "DoublePeak": "DP",
    "TriplePeak": "TP",
    "Interpulse": "IP",
    "Symmetric": "SYM",
    "Complicated": "COM",
    "Unclassified": "UC",
}
PROFILE = Select(title="Profile tags", options=sorted(profile_map.keys()), value="Unclassified")
pol_map = {
    "Linear": "LINP",
    "Circular": "CIRP",
    "PASwing": "PA",
    "RVM": "RVM",
    "Unclassified": "UC",
}
POL = Select(title="Polarization tags", options=sorted(pol_map.keys()), value="Unclassified")
frequency_map = {
    "FreqEvol": "FEVOL",
    "Scattered": "SCAT",
    "Scintillating": "SCIN",
    "Unclassified": "UC",
}
FREQ = Select(title="Frequency tags", options=sorted(frequency_map.keys()), value="Unclassified")
time_map = {
    "Nulling": "NULL",
    "Moding": "MODE",
    "StrongModulation": "MODU",
    "Stable": "STAB",
    "Drifting": "DRIFT",
    "Unclassified": "UC",
}
TIME = Select(title="Time tags", options=sorted(time_map.keys()), value="Unclassified")

#ADD CATEGORY TAGS HERE
#y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Number of Reviews")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], alpha=[],))

TOOLS = 'pan,wheel_zoom,xbox_select,box_zoom,lasso_select,undo,redo,save,reset'
TOOLTIPS=[
    ("JNAME","@JNAME"),
    ("P0", "@P0"),
    ("P1", "@P1"),
    ("DM", "@DM"),
    ("RM", "@RM"),
    ("PB", "@PB"),
    ("NGLT", "@NGLT"),
    ("CATEGORY","@CATEGORY")
]

p = figure(plot_height=1000, plot_width=900, title="", tooltips=TOOLTIPS, sizing_mode="scale_both",y_axis_type="log",
           x_axis_type="log",tools=TOOLS)
p.circle(x="P0", y="P1", source=source, size='size', color="color", line_color=None, fill_alpha="alpha")


def mapper(value):
    if value == "Gaussian":
        key = "GAU"
    if value == "DoublePeak":
        key = "DP"
    if value == "TriplePeak":
        key = "TP"
    if value == "Interpulse":
        key = "IP"
    if value == "Symmetric":
        key = "SYM"
    if value == "Complicated":
        key = "COM"
    if value == "Unclassified":
        key = "UC"
    if value == "Linear":
        key = "LINP"
    if value == "Circular":
        key = "CIRP"
    if value == "PASwing":
        key = "PA"
    if value == "RVM":
        key = "RVM"
    if value == "FreqEvol":
        key = "FEVOL"
    if value == "Scattered":
        key = "SCAT"
    if value == "Scintillating":
        key = "SCIN"
    if value == "Nulling":
        key = "NULL"
    if value == "Moding":
        key = "MODE"
    if value == "StrongModulation":
        key = "MODU"
    if value == "Stable":
        key = "STAB"
    if value == "Drifting":
        key = "DRIFT"

    return key

def update_textboxes(conv_f1,conv_age,conv_bsurf,conv_edot):
    F1_TEXT.text = "F1: "+str(conv_f1)+" x 1e-13"
    AGE_TEXT.text = "AGE: "+str(conv_age)+" Kyr"
    BSURF_TEXT.text = "BSURF: "+str(conv_bsurf)+" x 1e10"
    EDOT_TEXT.text = "EDOT: "+str(conv_edot)+" x 1e30"

def select_movies():
    assoc_val = ASSOC.value
    selected = df[
        (df.F0 >= F0.value) &
        (df.F1 >= F1.value) &
        (df.DM >= DM.value) &
        (df.RM >= RM.value) &
        (df.DIST >= DIST.value) &
        (df.AGE >= AGE.value) &
        (df.BSURF >= BSURF.value) &
        (df.EDOT >= EDOT.value)
    ]

    if (assoc_val != "NA"):
        selected = selected[selected.ASSOC.str.contains(assoc_val)==True]

    profile_key = mapper(PROFILE.value)
    pol_key = mapper(POL.value)
    freq_key = mapper(FREQ.value)
    time_key = mapper(TIME.value)

    if not profile_key == "UC":
        selected = selected[selected['CATEGORY'].str.contains(profile_key,na=False)]
    if not pol_key == "UC":
        selected = selected[selected['CATEGORY'].str.contains(pol_key,na=False)]
    if not freq_key == "UC":
        selected = selected[selected['CATEGORY'].str.contains(freq_key,na=False)]
    if not time_key == "UC":
        selected = selected[selected['CATEGORY'].str.contains(time_key,na=False)]


    #print profile_key,pol_key,freq_key,time_key

    conv_f1 = -10**(F1.value)
    conv_age = 10**(AGE.value)
    conv_bsurf = 10**(BSURF.value)
    conv_edot = 10**(EDOT.value)
    update_textboxes(conv_f1,conv_age,conv_bsurf,conv_edot)


    return selected

def update():
    df = select_movies()
    if not CATALOGUE.active:
        source_data(df)
    else:
        df = df.append(df_cat,sort=True)
        source_data(df)


def source_data(dataframe):

    df = dataframe
    p.xaxis.axis_label = "log(P0)"
    p.yaxis.axis_label = "log(P1)"
    p.xaxis.axis_label_text_font_size = '20pt'
    p.yaxis.axis_label_text_font_size = '20pt'
    p.xaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_text_font_style = "bold"
    p.xaxis.major_label_text_font_size = '13pt'
    p.yaxis.major_label_text_font_size = '13pt'

    p.title.text = "P-Pdot"
    p.title.text_font_size = '20pt'
    source.data = dict(
        P0=df["P0"],
        P1=df["P1"],
        color=df["color"],
        alpha=df["alpha"],
        size=df["size"],
        JNAME=df["JNAME"],
        BNAME=df["BNAME"],
        RAJ=df["RAJ"],
        DECJ=df["DECJ"],
        F0=df["F0"],
        F1=df["F1"],
        DM=df["DM"],
        RM=df["RM"],
        DIST=df["DIST"],
        ASSOC=df["ASSOC"],
        PB=df["PB"],
        BINCOMP=df["BINCOMP"],
        AGE=df["AGE"],
        BSURF=df["BSURF"],
        EDOT=df["EDOT"],
        NGLT=df["NGLT"],
        rm_MK=df["rm_MK"],
        dm_MK=df["dm_MK"],
        w50_MK=df["w50_MK"],
        w10_MK=df["w10_MK"],
        CATEGORY=df["CATEGORY"],
    )


controls = [F0,F1,DM,RM,DIST,AGE,BSURF,EDOT,ASSOC]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
inputs = column(*controls)

categories = [PROFILE,POL,FREQ,TIME]
for category in categories:
    category.on_change('value', lambda attr, old, new: update())
category_inputs = column(*categories)

text_boxes = [F1_TEXT,AGE_TEXT,BSURF_TEXT,EDOT_TEXT]
texts = column(*text_boxes)

UPDATE.on_click(update)

sliders_texts = column(inputs,texts,category_inputs,CATALOGUE)
plot_update = column(p,UPDATE)

l = layout([
    [plot_update,sliders_texts,USER_TEXT],
],sizing_mode='fixed')

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "TPA Classifier"
