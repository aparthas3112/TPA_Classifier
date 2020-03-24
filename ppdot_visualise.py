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

import os,sys,re
import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, layout, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, PreText, Button, Toggle, OpenURL, TapTool, MultiSelect
from bokeh.plotting import figure

import argparse
import shlex,glob


parser = argparse.ArgumentParser(description="P-Pdot visualiser for TPA pulsars")
parser.add_argument("-load",dest="load_pickle",help="Path to the Gsheet pickle file.",required=True)
parser.add_argument("-psrcat", dest="psrcat", help="Path to the full catalogue pickle file", required=True)
parser.add_argument("-tags", dest="tags", help="File with predefined tags", required=True)
args = parser.parse_args()

#Reading the two dataframes
df = pd.read_pickle(str(args.load_pickle))
df_cat = pd.read_pickle(str(args.psrcat))

#Setting attributes for df_cat
df_cat["color"] = "#7f8c8d"
df_cat["alpha"] = 0.6
df_cat["size"] = 7

#Set color and alpha
df["color"] = np.where(df["DM"] > 0, "#3498db", "grey")
df["alpha"] = np.where(df["DM"] > 0, 0.9, 0.25)
df['size'] = np.where(df["DM"] > 0, 9, 5)

#Replacing empty,NAN cells
df["ASSOC"].fillna("NA",inplace=True)
df["BNAME"].fillna("NA",inplace=True)
df["CATEGORY"].fillna("Unclassified",inplace=True)
df["COMMENTS"].fillna("NA",inplace=True)

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

#Converting to log-scale
df["F1"] = np.log10(abs(df["F1"]).astype("float64"))
df["AGE"] = np.log10(df["AGE"].astype("float64"))
df["BSURF"] = np.log10(df["BSURF"].astype("float64"))
df["EDOT"] = np.log10(df["EDOT"].astype("float64"))

#Getting pre-defined tag list
tags = {}
with open (args.tags, 'r') as f:
    for line in f:
        if "#" in line:
            key = line.split("#")[-1].rstrip()
            tags[key] = []
        else:
            tags[key].append(line.rstrip())

f.close()

# Create Input controls
F0 = Slider(title="Spin-frequency(F0)", value=df["F0"].min(), start=df["F0"].min(), end=df["F0"].max(), step=1)
F1 = Slider(title="Spin-frequency derivative(F1)(log)", value=df["F1"].min(), start=df["F1"].min(), end=df["F1"].max(), step=0.5)
DM = Slider(title="Dispersion measure(DM)", value=df["DM"].min(), start=df["DM"].min(), end=df["DM"].max(), step=0.5)
RM = Slider(title="Rotation measure(RM) - DISABLED", value=df["RM"].min(), start=df["RM"].min(), end=df["RM"].max(), step=0.5)
DIST = Slider(title="Distance", value=df["DIST"].min(), start=df["DIST"].min(), end=df["DIST"].max(), step=0.5)
AGE = Slider(title="Characteristic age(log)", value=df["AGE"].min(), start=df["AGE"].min(), end=df["AGE"].max(), step=0.5)
BSURF = Slider(title="Surface B-field(BSURF)(log)", value=df["BSURF"].min(), start=df["BSURF"].min(), end=df["BSURF"].max(), step=0.5)
EDOT = Slider(title="Energy loss(EDOT)(log)", value=df["EDOT"].min(), start=df["EDOT"].min(), end=df["EDOT"].max(), step=0.5)

ASSOC = Select(title="Association", options=df["ASSOC"].unique().tolist(), value="NA")

F1_TEXT = PreText(text='', width=500)
AGE_TEXT = PreText(text='', width=500)
BSURF_TEXT = PreText(text='', width=500)
EDOT_TEXT = PreText(text='', width=500)
status = PreText(text="""TODO:
1. Make P-Pdot plot more useful.
2. Add user comments.
3. Discuss classification tags.
4. Feedback.
5. Add histograms.
""", width=500)

CATALOGUE = Toggle(label="Toggle catalogue", width=300, button_type="success")
UPDATE = Button(label="Update",width=300)

PROFILE = MultiSelect(title="Profile tags", options=tags["PROFILE"], value=["Unclassified"],height=200)
POL = MultiSelect(title="Polarization tags", options=tags["POLARIZATION"], value=["Unclassified"],height=200)
FREQ = MultiSelect(title="Frequency tags", options=tags["FREQUENCY"], value=["Unclassified"],height=200)
TIME = MultiSelect(title="Time tags", options=tags["TIME"], value=["Unclassified"],height=200)
OBS = MultiSelect(title="Observation tags", options=tags["OBSERVATION"], value=["Unclassified"],height=200)


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
]

p = figure(plot_height=1000, plot_width=900, title="", tooltips=TOOLTIPS, sizing_mode="scale_both",y_axis_type="log",
           x_axis_type="log",tools=TOOLS)
p.circle(x="P0", y="P1", source=source, size='size', color="color", line_color=None, fill_alpha="alpha")

def update_textboxes(conv_f1,conv_age,conv_bsurf,conv_edot):
    F1_TEXT.text = "F1: "+str(conv_f1)+" x 1e-13"
    AGE_TEXT.text = "AGE: "+str(conv_age)+" Kyr"
    BSURF_TEXT.text = "BSURF: "+str(conv_bsurf)+" x 1e10"
    EDOT_TEXT.text = "EDOT: "+str(conv_edot)+" x 1e30"

def select_pulsars():
    assoc_val = ASSOC.value
    selected = df[
        (df.F0 >= F0.value) &
        (df.F1 >= F1.value) &
        (df.DM >= DM.value) &
        #(df.RM >= np.abs(RM.value)) &
        (df.DIST >= DIST.value) &
        (df.AGE >= AGE.value) &
        (df.BSURF >= BSURF.value) &
        (df.EDOT >= EDOT.value)
    ]

    if (assoc_val != "NA"):
        selected = selected[selected.ASSOC.str.contains(assoc_val)==True]

    profile_values = [str(r) for r in PROFILE.value]
    pol_values = [str(r) for r in POL.value]
    freq_values = [str(r) for r in FREQ.value]
    time_values = [str(r) for r in TIME.value]
    obs_values = [str(r) for r in OBS.value]

    print '|'.join(profile_values)
    if not "Unclassified" in profile_values:
        selected = selected[selected['CATEGORY'].str.contains('|'.join(profile_values),regex=True,na=False)]
    if not "Unclassified" in pol_values:
        selected = selected[selected['CATEGORY'].str.contains('|'.join(pol_values),regex=True,na=False)]
    if not "Unclassified" in freq_values:
        selected = selected[selected['CATEGORY'].str.contains('|'.join(freq_values),regex=True,na=False)]
    if not "Unclassified" in time_values:
        selected = selected[selected['CATEGORY'].str.contains('|'.join(time_values),regex=True,na=False)]
    if not "Unclassified" in obs_values:
        selected = selected[selected['CATEGORY'].str.contains('|'.join(obs_values),regex=True,na=False)]

    conv_f1 = -10**(F1.value)
    conv_age = 10**(AGE.value)
    conv_bsurf = 10**(BSURF.value)
    conv_edot = 10**(EDOT.value)
    update_textboxes(conv_f1,conv_age,conv_bsurf,conv_edot)


    return selected

def update():
    df = select_pulsars()
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
inputs_status = row(inputs,status)

categories = [PROFILE,POL,FREQ,TIME,OBS]
for category in categories:
    category.on_change('value', lambda attr, old, new: update())
category_inputs = column(PROFILE,POL)
category_inputs1 = column(FREQ,TIME)
category_inputs_all = row(category_inputs,category_inputs1,OBS)

text_boxes = [F1_TEXT,AGE_TEXT,BSURF_TEXT,EDOT_TEXT]
texts = column(*text_boxes)

UPDATE.on_click(update)

sliders_texts = column(inputs_status,texts,category_inputs_all,CATALOGUE)
plot_update = column(p,UPDATE)

l = layout([
    [plot_update,sliders_texts],
],sizing_mode='scale_width')

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "P-Pdot visualizer"
