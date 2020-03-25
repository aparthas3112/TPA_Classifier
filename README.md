## Brief instructions on running the various scripts and getting started with the classification. 

1. Inside the TPADocker and in `/home/psr/TPA/TPA_Classifier`
    ```
    bokeh serve classifier.py --port 5006 --args -psrlist tpa_psrs.list -tags classifier_tags.list
    ```
    This will launch the classifier in `localhost:5006` within the docker. Forward this to your local machine by running
     `ssh psr@localhost -p 2222 -L 5006:localhost:5006` 
    
    The classifier can then be viewed in `http://localhost:5006/classifier` in your local browser. 

2. After classification, run
```
python getcsv.py -psrlist tpa_psrs.list -psrcat psrcat_params.list -custom custom_params.list -save saved_queries/<somename>
```
This will create a set of files in the directory `saved_queries`, which will be used by the `ppdot_visualizer`. 

3. Now run the `ppdot-visualiser`,
```
bokeh serve ppdot_visualise.py --port 5007 --args -load saved_queries/<somename>.pckl -psrcat saved_queries/<somename>_fullcat.pckl -tags classifier_tags.list
``` 
This will launch it in `localhost:5007`, which is to be forwarded to your local machine as before. 
