# TPA_Classifier
Interactive web-based classifier for TPA pulsars observed with the MeerKAT radio telescope as part of MeerTime

## getcsv.py
```
usage: classifier_getcsv.py [-h] [-psrlist PSRLIST] [-psrcat PSRCAT_PARAMS]
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
  
`classifier_getcsv.py` is used to generate a dataframe that contains values for a set of psrcat parameters and the custom values for pulsar parameters measured with the MeerTIME data. 
 
 ## todataframe.py
 ```
 usage: gsheet_dataframe.py [-h] [-sheetid SHEETID] [-sheetname SHEETNAME]
                           [-save SAVE]

Generate dataframe from Google sheet (TPA Classifier)

optional arguments:
  -h, --help            show this help message and exit
  -sheetid SHEETID      ID for the google spreadsheet
  -sheetname SHEETNAME  Name for the google spreadsheet
  -save SAVE            Path and filename to save the downloaded GSheet as a
                        pckl
```
`gsheet_dataframe.py` is used to pull a gsheet from a URL and convert that to a dataframe that is then used by the classifier.                         
                       
                     
