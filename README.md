# Short Boi
This is a small application designed to provide information on stocks to help identify stocks that would be good to short.

## Setup:

This is a python 3 flask app, I typically run in debug mode, so I can see the changes after I save it. It is not intended or ready to be run in production environment for several reasons, but is perfectly safe enough to run locally.

### Pip:
use pip to install the following packages in a virtual env: `yf, flask, pandas, requests, matplotlib` [to setup virtual env](https://docs.python.org/3/library/venv.html#creating-virtual-environments)


### ENV:
This helps with the graph generation, without it you will get an error about saving the graphs to a specific file.
```
export MPLBACKEND='agg'
```

### Running the app:
Like I said above I just run this in debug mode. It does require you to enter the stocks you're interested in.. On line 41 in `app.py` you can see a ticker list pre-populated: 
```
return ['ISSC', 'AGBA', 'ONMD', 'OKLO', 'OLB', 'RYDE', 'APM']
```
change this to whatever you're interested and save the file.. Then boot up the server:
```
$ flash run --debug
```

That should be it! let me know if there are any issues in the issues tab, or feel free to PR fixes in. 
