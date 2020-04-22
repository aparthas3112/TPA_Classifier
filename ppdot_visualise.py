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
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, PreText, Button, Toggle, \
    OpenURL, TapTool, MultiSelect, RangeSlider, DataTable, DateFormatter, TableColumn, Panel, Tabs
from bokeh.plotting import figure
from bokeh.events import DoubleTap, Tap

import argparse
import shlex,glob


parser = argparse.ArgumentParser(description="P-Pdot visualiser for TPA pulsars")
parser.add_argument("-load",dest="load_pickle",help="Path to the Gsheet pickle file.",required=True)
parser.add_argument("-psrcat", dest="psrcat", help="Path to the full catalogue pickle file", required=True)
parser.add_argument("-tags", dest="tags", help="File with predefined tags", required=True)
args = parser.parse_args()

#Reading the two dataframes
df = pd.read_pickle(str(args.load_pickle)) #Custom TPA pulsar list
df_cat = pd.read_pickle(str(args.psrcat)) #Full catalogue pulsar list


##################################### FULL CATALOGUE ####################################
#Setting attributes for df_cat
df_cat["color"] = "#7f8c8d"
df_cat["alpha"] = 0.5
df_cat["size"] = 6
#Replacing empty,NAN cells
df_cat["ASSOC"].fillna("NA",inplace=True)
df_cat["BNAME"].fillna("NA",inplace=True)
df_cat["TYPE"].fillna("NA",inplace=True)
df_cat["DM"].fillna("0.0",inplace=True)
df_cat["RM"].fillna("0.0",inplace=True)
df_cat["DIST"].fillna("0.0",inplace=True)

#Normalising relevant columns
df_cat["F1"] = df_cat["F1"]/10**-13
df_cat["AGE"] = df_cat["AGE"]/10**3
df_cat["BSURF"] = df_cat["BSURF"]/10**10
df_cat["EDOT"] = df_cat["EDOT"]/10**30

#Converting to log-scale
df_cat["F0"] = np.log10(df_cat["F0"]).astype("float64")
df_cat["F1"] = np.log10(abs(df_cat["F1"]).astype("float64"))
df_cat["AGE"] = np.log10(df_cat["AGE"].astype("float64"))
df_cat["BSURF"] = np.log10(df_cat["BSURF"].astype("float64"))
df_cat["EDOT"] = np.log10(df_cat["EDOT"].astype("float64"))


##################################### TPA PULSARS ####################################
#Set color and alpha
df["color"] = np.where(df["DM"] > 0, "#3498db", "grey")
df["alpha"] = np.where(df["DM"] > 0, 0.9, 0.25)
df['size'] = np.where(df["DM"] > 0, 9, 5)

#Replacing empty,NAN cells
df["ASSOC"].fillna("NA",inplace=True)
df["BNAME"].fillna("NA",inplace=True)
df["TYPE"].fillna("NA",inplace=True)
df["CATEGORY"].fillna("Unclassified",inplace=True)
df["COMMENTS"].fillna("NA",inplace=True)
df["DM"].fillna("0.0",inplace=True)
df["RM"].fillna("0.0",inplace=True)
df["DIST"].fillna("0.0",inplace=True)

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
df["F0"] = np.log10(df["F0"]).astype("float64")
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
F0 = RangeSlider(title="Spin-frequency(F0)(log)", value=(df["F0"].min(),df["F0"].max()), start=df["F0"].min(), end=df["F0"].max(), step=0.1)
F1 = RangeSlider(title="Spin-frequency derivative(F1)(log)", value=(df["F1"].min(),df["F1"].max()), start=df["F1"].min(), end=df["F1"].max(), step=0.1)
DM = RangeSlider(title="Dispersion measure(DM)", value=(df["DM"].min(),df["DM"].max()), start=df["DM"].min(), end=df["DM"].max(), step=0.5)
RM = RangeSlider(title="Rotation measure(RM) - DISABLED", value=(df["RM"].min(),df["RM"].max()), start=df["RM"].min(), end=df["RM"].max(), step=0.5)
DIST = RangeSlider(title="Distance", value=(df["DIST"].min(),df["DIST"].max()), start=df["DIST"].min(), end=df["DIST"].max(), step=0.5)
AGE = RangeSlider(title="Characteristic age(log)", value=(df["AGE"].min(),df["AGE"].max()), start=df["AGE"].min(), end=df["AGE"].max(), step=0.5)
BSURF = RangeSlider(title="Surface B-field(BSURF)(log)", value=(df["BSURF"].min(),df["BSURF"].max()), start=df["BSURF"].min(), end=df["BSURF"].max(), step=0.5)
EDOT = RangeSlider(title="Energy loss(EDOT)(log)", value=(df["EDOT"].min(),df["EDOT"].max()), start=df["EDOT"].min(), end=df["EDOT"].max(), step=0.5)

ASSOC = MultiSelect(title="Association", options=df["ASSOC"].unique().tolist(), value=["NA"])
TYPE = MultiSelect(title="Type", options=df["TYPE"].unique().tolist(), value=["NA"])

SUMMARY_TEXT = PreText(text='', width=500)
RESET_TOGGLE = Toggle(label="Reset selections", width=150, button_type='warning')

CATALOGUE = Toggle(label="Toggle catalogue", width=150, button_type="warning")
UPDATE = Button(label="Update",width=150, button_type="success")

PROFILE = MultiSelect(title="Profile tags", options=tags["PROFILE"], value=["Unclassified"],height=200)
POL = MultiSelect(title="Polarization tags", options=tags["POLARIZATION"], value=["Unclassified"],height=200)
FREQ = MultiSelect(title="Frequency tags", options=tags["FREQUENCY"], value=["Unclassified"],height=200)
TIME = MultiSelect(title="Time tags", options=tags["TIME"], value=["Unclassified"],height=200)
OBS = MultiSelect(title="Observation tags", options=tags["OBSERVATION"], value=["Unclassified"],height=200)

URL_TEXT = Div(text='',width=500)

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], alpha=[],))
source_all = ColumnDataSource(data=dict(x=[], y=[], color=[], alpha=[],))

selected_plot_source = ColumnDataSource(data=dict(jname=[],profile=[],pol=[],freq=[],time=[],obs=[],comments=[]))

TOOLS = 'pan,wheel_zoom,xbox_select,box_zoom,lasso_select,undo,redo,save,reset,tap'
TOOLTIPS=[
    ("JNAME","@JNAME"),
    ("P0", "@P0"),
    ("P1", "@P1"),
    ("DM", "@DM"),
    ("RM", "@RM"),
    ("NGLT", "@NGLT"),
]

TOOLTIPS_MINIMAL=[
    ("JNAME","@JNAME"),
    ("DM", "@DM"),
    ("RM", "@RM"),
]


p = figure(plot_height=800, plot_width=700, title="", tooltips=TOOLTIPS_MINIMAL, sizing_mode="scale_width",y_axis_type="log",
           x_axis_type="log",tools=TOOLS)
p.circle(x="P0", y="P1", source=source, size='size', color="color", line_color=None, fill_alpha="alpha")
p.circle(x="P0", y="P1", source=source_all, size='size', color="color", line_color=None, fill_alpha="alpha")


#Sub-figures
x_axis = Select(title="X-axis (also used for histograms)",options=list(df.columns.values),value='P0')
y_axis = Select(title="Y-axis", options=list(df.columns.values),value='P1')
x_axis_scale = Select(title="XScale",options=["log","linear"],value='log')
y_axis_scale = Select(title="YScale", options=["log","linear"],value='log')

scatter = figure(plot_height=400, plot_width=650, title="", sizing_mode="scale_width",tools=TOOLS)
scatter.circle(x='x', y= 'y', source=source, size=6, color="color", line_color=None, fill_alpha=0.9)
tab1 = Panel(child=scatter,title="Scatter plot")

histogram_source = ColumnDataSource(data=dict(hist=[],edges_left=[],edges_right=[],hist_all=[],edges_left_all=[],
                                              edges_right_all=[]))
histogram = figure(plot_height=400, plot_width=650, title="", sizing_mode="scale_width",tools=TOOLS)

histogram.quad(top='hist', bottom=0, left='edges_left', right='edges_right', source=histogram_source, fill_color="#e74c3c",
               line_color=None, alpha=0.9)

tab2 = Panel(child=histogram,title="Histogram plot")

tabs = Tabs(tabs=[tab2,tab1])

#Table
table_columns=[
    TableColumn(field="jname", title="PSRNAME"),
    TableColumn(field="profile", title="PROFILE"),
    TableColumn(field="pol", title="POLARIZATION"),
    TableColumn(field="freq", title="FREQUENCY"),
    TableColumn(field="time", title="TIME"),
    TableColumn(field="obs", title="OBSERVATION"),
    TableColumn(field="comments", title="COMMENTS"),
]
SELECTION_TABLE = DataTable(source=selected_plot_source, columns=table_columns,width=900,height=600,
                            fit_columns=True,reorderable=True,scroll_to_selection=True,sortable=True,
                            selectable=True, sizing_mode='fixed')


def get_tags(dataframe):
    profile_tags = []
    pol_tags=[]
    freq_tags=[]
    time_tags=[]
    obs_tags=[]

    tag_list = dataframe["CATEGORY"].tolist()

    for item in tag_list:
        if not item == "Unclassified":
            tmp = item.split(";")
            for item1 in tmp:
                category_class = item1.split(':')
                if category_class[0] == "PROFILE":
                    profile_tags.append(category_class[-1].split("+"))

                elif category_class[0] == "POLARIZATION":
                    pol_tags.append(category_class[-1].split("+"))

                elif category_class[0] == "FREQUENCY":
                    freq_tags.append(category_class[-1].split("+"))

                elif category_class[0] == "TIME":
                    time_tags.append(category_class[-1].split("+"))

                elif category_class[0] == "OBSERVATION":
                    obs_tags.append(category_class[-1].split("+"))


    profile_tags = np.unique([item for sublist in profile_tags for item in sublist])
    pol_tags = np.unique([item for sublist in pol_tags for item in sublist])
    freq_tags = np.unique([item for sublist in freq_tags for item in sublist])
    time_tags = np.unique([item for sublist in time_tags for item in sublist])
    obs_tags = np.unique([item for sublist in obs_tags for item in sublist])

    profile_tags = [str(x).rstrip() for x in profile_tags]
    pol_tags = [str(x).rstrip() for x in pol_tags]
    freq_tags = [str(x).rstrip() for x in freq_tags]
    time_tags = [str(x).rstrip() for x in time_tags]
    obs_tags = [str(x).rstrip() for x in obs_tags]

    return (profile_tags, pol_tags, freq_tags, time_tags, obs_tags)


def update_summary(conv_f0_lower, conv_f0_upper,conv_f1_lower, conv_f1_upper, conv_age_lower, conv_age_upper, conv_bsurf_lower, conv_bsurf_upper, conv_edot_lower, conv_edot_upper, conv_rm_lower, conv_rm_upper, conv_dm_lower, conv_dm_upper, conv_dist_lower, conv_dist_upper, npulsars):
    SUMMARY_TEXT.text = """
    Number of TPA pulsars in P-Pdot: {16} \n
    F0: {0} Hz to {1} Hz \n
    F1: ({2} to {3}) x1e-13 s^-2 \n
    AGE: {4} Kyr to {5} Kyr \n
    BSURF: ({6} to {7}) x1e10 G \n
    EDOT: ({8} to {9}) x1e30 ergs/s \n
    RM: {10} rad m^-2 to {11} rad m^-2 \n
    DM: {12} cm^-3 pc to {13} cm^-3 pc \n
    DIST: {14} kpc to {15} kpc \n
    """.format(conv_f0_lower, conv_f0_upper,conv_f1_lower, conv_f1_upper, conv_age_lower, conv_age_upper, conv_bsurf_lower, conv_bsurf_upper, conv_edot_lower, conv_edot_upper, conv_rm_lower, conv_rm_upper, conv_dm_lower, conv_dm_upper, conv_dist_lower, conv_dist_upper, npulsars)

def select_pulsars():
    selected = df[
        (df.F0 >= F0.value[0]) & (df.F0 <= F0.value[1]) &
        (df.F1 >= F1.value[0]) & (df.F1 <= F1.value[1]) &
        (df.DM >= DM.value[0]) & (df.DM <= DM.value[1]) &
        (df.RM >= RM.value[0]) & (df.RM <= RM.value[1]) &
        (df.DIST >= DIST.value[0]) & (df.DIST <= DIST.value[1]) &
        (df.AGE >= AGE.value[0]) & (df.AGE <= AGE.value[1]) &
        (df.BSURF >= BSURF.value[0]) & (df.BSURF <= BSURF.value[1]) &
        (df.EDOT >= EDOT.value[0]) & (df.EDOT <= EDOT.value[1])
    ]

    assoc_vals = [str(r) for r in ASSOC.value]
    type_vals = [str(r) for r in TYPE.value]

    if not "NA" in assoc_vals:
        selected = selected[selected['ASSOC'].str.contains('|'.join(assoc_vals),regex=True,na=False)]
    if not "NA" in type_vals:
        selected = selected[selected['TYPE'].str.contains('|'.join(type_vals),regex=True,na=False)]

    #Obtaining selected tags
    profile_values = [str(r) for r in PROFILE.value]
    pol_values = [str(r) for r in POL.value]
    freq_values = [str(r) for r in FREQ.value]
    time_values = [str(r) for r in TIME.value]
    obs_values = [str(r) for r in OBS.value]

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

    conv_f0_lower = 10 ** (selected["F0"].min())
    conv_f0_upper = 10 ** (selected["F0"].max())
    conv_f1_lower = -10**(selected["F1"].min())
    conv_f1_upper = -10 ** (selected["F1"].max())
    conv_age_lower = 10**(selected["AGE"].min())
    conv_age_upper = 10 ** (selected["AGE"].max())
    conv_bsurf_lower = 10**(selected["BSURF"].min())
    conv_bsurf_upper = 10**(selected["BSURF"].max())
    conv_edot_lower = 10**(selected["EDOT"].min())
    conv_edot_upper = 10**(selected["EDOT"].max())


    #Updating the actual range sliders
    F0.value=(selected["F0"].min(),selected["F0"].max())
    F1.value=(selected["F1"].min(),selected["F1"].max())
    DM.value=(selected["DM"].min(),selected["DM"].max())
    RM.value=(selected["RM"].min(),selected["RM"].max())
    DIST.value=(selected["DIST"].min(),selected["DIST"].max())
    AGE.value=(selected["AGE"].min(),selected["AGE"].max())
    BSURF.value=(selected["BSURF"].min(),selected["BSURF"].max())
    EDOT.value=(selected["EDOT"].min(),selected["EDOT"].max())
    ASSOC.options=selected["ASSOC"].unique().tolist()
    TYPE.options = selected["TYPE"].unique().tolist()

    #Return profile, pol, freq, time, obs, na
    tags = get_tags(selected)
    PROFILE.options = np.unique(tags[0]).tolist()
    POL.options = np.unique(tags[1]).tolist()
    FREQ.options = np.unique(tags[2]).tolist()
    TIME.options = np.unique(tags[3]).tolist()
    OBS.options = np.unique(tags[4]).tolist()

    update_summary(conv_f0_lower, conv_f0_upper, conv_f1_lower, conv_f1_upper ,conv_age_lower, conv_age_upper, conv_bsurf_lower, conv_bsurf_upper, conv_edot_lower, conv_edot_upper,
                   selected["RM"].min(), selected["RM"].max(), selected["DM"].min(), selected["DM"].max(), selected["DIST"].min(), selected["DIST"].max(), len(selected))


    return selected


def reset_selection():
    #Reset the range sliders
    F0.value=(df["F0"].min(),df["F0"].max())
    F1.value=(df["F1"].min(),df["F1"].max())
    DM.value=(df["DM"].min(),df["DM"].max())
    RM.value=(df["RM"].min(),df["RM"].max())
    DIST.value=(df["DIST"].min(),df["DIST"].max())
    AGE.value=(df["AGE"].min(),df["AGE"].max())
    BSURF.value=(df["BSURF"].min(),df["BSURF"].max())
    EDOT.value=(df["EDOT"].min(),df["EDOT"].max())
    ASSOC.options=df["ASSOC"].unique().tolist()
    TYPE.options = df["TYPE"].unique().tolist()

    ASSOC.value=["NA"]
    TYPE.value=["NA"]

    conv_f0_lower = 10 ** (df["F0"].min())
    conv_f0_upper = 10 ** (df["F0"].max())
    conv_f1_lower = -10**(df["F1"].min())
    conv_f1_upper = -10 ** (df["F1"].max())
    conv_age_lower = 10**(df["AGE"].min())
    conv_age_upper = 10 ** (df["AGE"].max())
    conv_bsurf_lower = 10**(df["BSURF"].min())
    conv_bsurf_upper = 10**(df["BSURF"].max())
    conv_edot_lower = 10**(df["EDOT"].min())
    conv_edot_upper = 10**(df["EDOT"].max())

    #Reset the tags
    PROFILE.options=tags["PROFILE"]
    PROFILE.value=["Unclassified"]
    POL.options=tags["POLARIZATION"]
    POL.value = ["Unclassified"]
    FREQ.options=tags["FREQUENCY"]
    FREQ.value = ["Unclassified"]
    TIME.options=tags["TIME"]
    TIME.value = ["Unclassified"]
    OBS.options=tags["OBSERVATION"]
    OBS.value = ["Unclassified"]

    update_summary(conv_f0_lower, conv_f0_upper, conv_f1_lower, conv_f1_upper ,conv_age_lower, conv_age_upper, conv_bsurf_lower, conv_bsurf_upper, conv_edot_lower, conv_edot_upper,
                   df["RM"].min(), df["RM"].max(), df["DM"].min(), df["DM"].max(), df["DIST"].min(), df["DIST"].max(), len(df))


    #selected_plot_source.data = dict(jname=[], profile=[], pol=[], freq=[], time=[], obs=[], comments=[])
    return df


def update():
    if not RESET_TOGGLE.active:
        df = select_pulsars()
    elif RESET_TOGGLE.active:
        df = reset_selection()

    if not CATALOGUE.active:
        source_data(df,df)
    else:
        #df_all = df.append(df_cat,sort=True)
        source_data(df,df_cat)

def source_data(dataframe,dataframe1):

    df = dataframe
    df_cat = dataframe1

    #Ppdot plot
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

    #Scatter plot
    x_name = str(x_axis.value)
    y_name = str(y_axis.value)
    scatter.xaxis.axis_label = "{0}({1})".format(x_name,x_axis_scale.value)
    scatter.yaxis.axis_label = "{0}({1})".format(y_name,y_axis_scale.value)
    scatter.xaxis.axis_label_text_font_size = '12pt'
    scatter.yaxis.axis_label_text_font_size = '12pt'
    scatter.xaxis.axis_label_text_font_style = "bold"
    scatter.yaxis.axis_label_text_font_style = "bold"
    scatter.xaxis.major_label_text_font_size = '12pt'
    scatter.yaxis.major_label_text_font_size = '12pt'

    scatter.title.text = "{0} vs {1}".format(x_name,y_name)
    scatter.title.text_font_size = '10pt'

    x_values = df[x_name]
    if x_axis_scale.value == "log":
        x_values = np.log10(df[x_name].astype("float64"))

    y_values = df[y_name]
    if y_axis_scale.value == "log":
        y_values = np.log10(df[y_name].astype("float64"))


    #Histogram plot
    histogram.xaxis.axis_label = "{0}".format(x_name)
    histogram.yaxis.axis_label = "Pr(x)"
    histogram.xaxis.axis_label_text_font_size = '12pt'
    histogram.yaxis.axis_label_text_font_size = '12pt'
    histogram.xaxis.axis_label_text_font_style = "bold"
    histogram.yaxis.axis_label_text_font_style = "bold"
    histogram.xaxis.major_label_text_font_size = '12pt'
    histogram.yaxis.major_label_text_font_size = '12pt'

    df[x_name] = df[x_name].astype("float64")
    hist, edges = np.histogram(df[x_name][~np.isnan(df[x_name])],density=True,bins='auto')

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
        TYPE=df["TYPE"],
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
        x=x_values,
        y=y_values,
    )

    source_all.data = dict(
        P0=df_cat["P0"],
        P1=df_cat["P1"],
        color=df_cat["color"],
        alpha=df_cat["alpha"],
        size=df_cat["size"],
        JNAME=df_cat["JNAME"],
        BNAME=df_cat["BNAME"],
        RAJ=df_cat["RAJ"],
        DECJ=df_cat["DECJ"],
        F0=df_cat["F0"],
        F1=df_cat["F1"],
        DM=df_cat["DM"],
        RM=df_cat["RM"],
        DIST=df_cat["DIST"],
        ASSOC=df_cat["ASSOC"],
        TYPE=df_cat["TYPE"],
        PB=df_cat["PB"],
        BINCOMP=df_cat["BINCOMP"],
        AGE=df_cat["AGE"],
        BSURF=df_cat["BSURF"],
        EDOT=df_cat["EDOT"],
        NGLT=df_cat["NGLT"],
    )

    histogram_source.data = dict(
        hist=hist,
        edges_left=edges[:-1],
        edges_right=edges[1:],
    )

    if len(source.selected.indices) > 0:
        selected_plot =  df.iloc[source.selected.indices,:]
        selected_tags = selected_plot["CATEGORY"].tolist()
        name = []
        profile =[]
        pol = []
        freq = []
        time = []
        obs = []
        comments=[]
        for num,item in enumerate(selected_tags):
            name.append(selected_plot["JNAME"].iloc[num])
            comments.append(selected_plot["COMMENTS"].iloc[num])
            if not item == "Unclassified":
                tmp = item.split(";")
                for item1 in tmp:
                    item2 = item1.split(":")
                    if item2[0] == "PROFILE":
                        profile.append(item2[-1].split(":")[-1])
                    if item2[0] == "POLARIZATION":
                        pol.append(item2[-1].split(":")[-1])
                    if item2[0] == "FREQUENCY":
                        freq.append(item2[-1].split(":")[-1])
                    if item2[0] == "TIME":
                        time.append(item2[-1].split(":")[-1])
                    if item2[0] == "OBSERVATION":
                        obs.append(item1.split(":")[-1])
            else:
                profile.append("Unclassified")
                pol.append("Unclassified")
                freq.append("Unclassified")
                time.append("Unclassified")
                obs.append("Unclassified")

        selected_plot_source.data = dict(jname=name,profile=profile,pol=pol,
                                         freq=freq,time=time,obs=obs,
                                         comments=comments)

    if len(selected_plot_source.selected.indices) > 0:
        psrname = selected_plot_source.data["jname"][selected_plot_source.selected.indices[0]]
        URL_TEXT.text = """<a href='https://www.atnf.csiro.au/people/joh414/meerkat/{0}.html'>
        https://www.atnf.csiro.au/people/joh414/meerkat/{0}.html</a>""".format(psrname)



controls = [F0,F1,DM,RM,DIST,AGE,BSURF,EDOT,ASSOC,TYPE]
#for control in controls:
#    control.on_change('value', lambda attr, old, new: update())
inputs = column(*controls)

categories = [PROFILE,POL,FREQ,TIME,OBS]
#for category in categories:
#    category.on_change('value', lambda attr, old, new: update())
category_inputs = column(PROFILE,POL)
category_inputs1 = row(FREQ,TIME,OBS)
#category_inputs_all = column(category_inputs,category_inputs1)


SUMMARY = column(SUMMARY_TEXT,SELECTION_TABLE)
#sliders_textboxes = row(inputs,SUMMARY)
buttons_toggles_row = row(RESET_TOGGLE,CATALOGUE,UPDATE,URL_TEXT)

inputs_category1 = column(inputs,category_inputs)
inputs_category1_summary_row = row(inputs_category1,SUMMARY)
sliders_texts = column(inputs_category1_summary_row,category_inputs1,buttons_toggles_row)

UPDATE.on_click(update)

p.on_event(Tap,update)
selected_plot_source.selected.on_change('indices', lambda attr, old, new: update())

scatter_axes = row(x_axis,y_axis)
scatter_axes_scale = row(x_axis_scale,y_axis_scale)
figures = column(p,scatter_axes,scatter_axes_scale,tabs)

l = layout([
    [figures,sliders_texts],
],sizing_mode='scale_width')

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "P-Pdot visualizer"
