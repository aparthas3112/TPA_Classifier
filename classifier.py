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
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure

import argparse
import shlex,glob


parser = argparse.ArgumentParser(description="Interactive classifier for TPA pulsars")
parser.add_argument("-load",dest="load_pickle",help="Path to the Gsheet pickle file.",required=True)
args = parser.parse_args()

df = pd.read_pickle(str(args.load_pickle))

print df.columns

#Set color and alpha
df["color"] = np.where(df["DM"] > 0, "#3498db", "grey")
df["alpha"] = np.where(df["DM"] > 0, 0.9, 0.25)

#Replacing empty,NAN cells
df["ASSOC"].fillna("NA",inplace=True)
df["BNAME"].replace("","NA",inplace=True)
df["CATEGORY"].replace("","NA",inplace=True)
df["COMMENTS"].replace("","NA",inplace=True)

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

# Create Input controls
F0 = Slider(title="Spin-frequency(F0)", value=df["F0"].median(), start=df["F0"].min(), end=df["F0"].max(), step=1)
F1 = Slider(title="Spin-frequency derivative(F1)", value=abs(df["F1"].median()), start=abs(df["F1"].min()), end=abs(df["F1"].max()), step=1)
DM = Slider(title="Dispersion measure(DM)", value=df["DM"].median(), start=df["DM"].min(), end=df["DM"].max(), step=1)
RM = Slider(title="Rotation measure(RM)", value=df["RM"].median(), start=df["RM"].min(), end=df["RM"].max(), step=1)
DIST = Slider(title="Distance", value=df["DIST"].median(), start=df["DIST"].min(), end=df["DIST"].max(), step=1)
AGE = Slider(title="Characteristic age", value=df["AGE"].median(), start=df["AGE"].min(), end=df["AGE"].max(), step=1)
BSURF = Slider(title="Surface B-field(BSURF)", value=df["BSURF"].median(), start=df["BSURF"].min(), end=df["BSURF"].max(), step=1)
EDOT = Slider(title="Energy loss(EDOT)", value=df["EDOT"].median(), start=df["EDOT"].min(), end=df["EDOT"].max(), step=1)
NGLT = Slider(title="Number of glitches", value=df["NGLT"].median(), start=df["NGLT"].min(), end=df["NGLT"].max(), step=1)
PB = Slider(title="Orbital period(PB)", value=df["PB"].median(), start=df["PB"].min(), end=df["PB"].max(), step=1)

ASSOC = Select(title="Association", options=df["ASSOC"].unique().tolist(), value="NA")


#ADD CATEGORY TAGS HERE
#y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Number of Reviews")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], alpha=[],))

TOOLTIPS=[
    ("JNAME","@JNAME"),
    ("RAJ", "@RAJ"),
    ("DECJ", "@DECJ"),
    ("P0", "@P0"),
    ("P1", "@P1")
]

p = figure(plot_height=400, plot_width=600, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both",y_axis_type="log",
           x_axis_type="log")
p.circle(x="P0", y="P1", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")


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
        (df.EDOT >= EDOT.value) &
        (df.NGLT >= NGLT.value) &
        (df.PB >= PB.value)
    ]

    if (assoc_val != "NA"):
        selected = selected[selected.ASSOC.str.contains(assoc_val)==True]

    return selected


def update():
    #df = select_movies()
    print df
    p.xaxis.axis_label = r"$P0$"
    p.yaxis.axis_label = r"$P1$"
    p.title.text = r"$P$-$\dot{P}$"
    source.data = dict(
        P0=df["P0"],
        P1=df["P1"],
        color=df["color"],
        alpha=df["alpha"],
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
    )

controls = [F0,F1,DM,RM,DIST,AGE,BSURF,EDOT,NGLT,PB]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320, height=1000)
inputs.sizing_mode = "fixed"
l = layout([
    [p,inputs],
], sizing_mode="scale_both")

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Movies"
