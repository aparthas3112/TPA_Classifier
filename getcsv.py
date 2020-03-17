#!/usr/bin/env python

import os,sys
import shlex,glob
import numpy as np
import pandas as pd
import argparse
from psrqpy import QueryATNF

parser = argparse.ArgumentParser(description="Generate CSV for TPA Classifier")
parser.add_argument("-psrlist",dest="psrlist",help="File with list of TPA pulsars")
parser.add_argument("-psrcat",dest="psrcat_params",help="File with list of psrcat parameters")
parser.add_argument("-custom",dest="custom_params",help="File with list of paths of measured parameters")
parser.add_argument("-save",dest="save",help="Path with filename to save query (pckl and csv)")
parser.add_argument("-load",dest="load",help="Load previous query into dataframe")
args = parser.parse_args()

if args.load:
    df = pd.read_pickle(args.load)
else:
    psrlist = np.genfromtxt(args.psrlist,dtype=str,comments="#",autostrip=True)
    psrcat_params = np.genfromtxt(args.psrcat_params,dtype=str,comments="#",autostrip=True)

    psrlist = psrlist.tolist()
    psrcat_params = psrcat_params.tolist()

    query = QueryATNF(psrs=psrlist,params=psrcat_params)

    #Saving the entire catalogue too
    df_cat = query.catalogue
    df_cat = df_cat[['JNAME','BNAME','RAJ','RAJ_ERR','DECJ','DECJ_ERR','F0','F0_ERR','F1','F1_ERR','P0','P0_ERR',
    'P1','P1_ERR','DM','DM_ERR','RM','RM_ERR','DIST','ASSOC','PB','PB_ERR','BINCOMP','AGE',
    'BSURF','EDOT','NGLT']]
    #Removing TPA pulsars from the full catalogue pickle file
    indices = df_cat[df_cat["JNAME"].isin(psrlist)].index
    df_cat.drop(indices,inplace=True)
    if args.save:
        df_cat.to_pickle(args.save+"_fullcat.pckl")

    df = query.pandas
    #Rearranging the dataframe columns
    df = df[['JNAME','BNAME','RAJ','RAJ_ERR','DECJ','DECJ_ERR','F0','F0_ERR','F1','F1_ERR','P0','P0_ERR',
    'P1','P1_ERR','DM','DM_ERR','RM','RM_ERR','DIST','ASSOC','PB','PB_ERR','BINCOMP','AGE',
    'BSURF','EDOT','NGLT']]

    #print df.columns

    #Creating dataframes for custom measured parameters using files in "custom_params" argument.
    custom_files = np.genfromtxt(args.custom_params,dtype=str,comments="#",autostrip=True)

    for file in custom_files:
        fname = file[0]
        fpath = file[-1]

        colname = fname.split("_")[0]+"_MK"
        custom_df = pd.read_csv(fpath,sep=" ",names=['JNAME',colname],comment="#")

        df = pd.merge(df,custom_df,on='JNAME',how='outer')

    if args.save:
        df.to_pickle(args.save+".pckl")
        df.to_csv(args.save+".csv",index=False)

print df

