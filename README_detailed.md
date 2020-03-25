# TPA_Classifier
Interactive web-based classifier for TPA pulsars observed with the MeerKAT radio telescope as part of MeerTime

## getcsv.py
```
usage: getcsv.py [-h] [-psrlist PSRLIST] [-psrcat PSRCAT_PARAMS]
                 [-custom CUSTOM_PARAMS] [-save SAVE] [-load LOAD]

Generate CSV for TPA Classifier

optional arguments:
  -h, --help            show this help message and exit
  -psrlist PSRLIST      File with list of TPA pulsars
  -psrcat PSRCAT_PARAMS
                        File with list of psrcat parameters
  -custom CUSTOM_PARAMS
                        File with list of paths of measured parameters
  -save SAVE            Path with filename to save query (pckl and csv)
  -load LOAD            Load previous query into dataframe
 ```
 
Example usage for `getcsv.py`:
`python getcsv.py -psrlist tpa_psrs.list -psrcat psrcat_params.list -custom custom_params.list -save saved_queries/classifier` 

This will query `psrcat` for the list of parameters mentioned in `psrcat_params.list` for the list of pulsars in `tpa_psrs.list` and generate a pandas dataframe. Then it will also look in the files mentioned in `custom_params.list` and create appropriate entries in the dataframe. For example, pulsars with custom RMs, DMs etc. It will then convert this dataframe into a csv file and save three different files in the specified path (in this case, `saved_queries/` with the prefix `classifier`. The three files are `classifier.pckl` (a pickle format file), `classifier.csv` and a `classifier_fullcat.pckl`. The last file is a list of all pulsars from the catalogue excluding the ones in `tpa_psrs.list`. 
 
 While testing this code, please import the generated csv file into a new Google spreadhseet and enable link-based sharing options before running the next script. 
 
 ## todataframe.py
 ```
 usage: todataframe.py [-h] [-sheetid SHEETID] [-sheetname SHEETNAME]
                      [-save SAVE]

Generate dataframe from Google sheet (TPA Classifier)

optional arguments:
  -h, --help            show this help message and exit
  -sheetid SHEETID      ID for the google spreadsheet
  -sheetname SHEETNAME  Name for the google spreadsheet
  -save SAVE            Path and filename to save the downloaded GSheet as a
                        pckl
```
`todataframe.py` is used to pull a Google spreadsheet from a specified URL and convert that to a dataframe which is then used by the classifier.                    

Example usage for `todataframe.py`:
`python todataframe.py -sheetid <sheetID> -sheetname <sheetName> -save fromGoogleSheets/classifier_gsheet`

If the URL for the spreadsheet is the following: 
`https://docs.google.com/spreadsheets/d/1THISISFAKEShcQpBP7R3DzZaRWan3MCTWGpjc-0fRANDOM!urhg/edit#gid=0`, then the `sheetID` is `1THISISFAKEShcQpBP7R3DzZaRWan3MCTWGpjc-0fRANDOM!urhg` and the `sheetName` is the title of the spreadsheet. 

This will download the relevant Google spreadsheet and convert it into a pickle format, which will be then used by the classifier. 

## classifier.py

`classifier.py` is an interactive web-based classifier. It is based on a python visualisation library called `bokeh`. To spawn an instance of the web-page, run:
` bokeh serve classifier.py --args -load fromGoogleSheets/classifier_gsheet.pckl -psrcat saved_queries/classifier_fullcat.pckl` 

This loads the downloaded google spreadsheet and the full catalogue pickle file and starts up a server in `localhost:5006/classifier`. 

If you are running this directly on a local machine, then just open up the URL in a browser. If you are instead running this inside a virtual instance, for example, like a docker container, then you need to forward the ports. This is dependent on the virtual instance. 

Using with `MeerDock`: If you are running this inside `MeerDock`, then just run, 
`ssh psr@localhost -p 2222 -L 5006:localhost:5006` (locally) and go to `localhost:5006` in a browser on your local machine. 

                
                
                     
