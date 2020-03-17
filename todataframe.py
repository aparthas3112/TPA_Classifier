#!/usr/bin/env python

import os,sys
import shlex,glob
import numpy as np
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description="Generate dataframe from Google sheet (TPA Classifier)")
parser.add_argument("-sheetid",dest="sheetid",help="ID for the google spreadsheet")
parser.add_argument("-sheetname",dest="sheetname",help="Name for the google spreadsheet")
parser.add_argument("-save",dest="save",help="Path and filename to save the downloaded GSheet as a pckl")
args = parser.parse_args()

googleSheetId = str(args.sheetid)
worksheetName = str(args.sheetname)
URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
	googleSheetId,
	worksheetName
)

df = pd.read_csv(URL,sep=",",comment="#")

if args.save:
    df.to_pickle(args.save+".pckl")
