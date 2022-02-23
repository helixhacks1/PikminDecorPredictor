# Pikmin Decor Predictor
A collection of scripts used to analyze Pikmin Bloom decor data and predict what tags are used to generate decors. Python 3.6+ is required to run the scripts.

## predict_decors.py
Script that takes a latitude and longitude as required inputs, and attempts to
output potential Pikmin Bloom decors at that location. Optionally, a radius and
a date may be given to narrow down results. Also, API keys from developer
accounts must be given to query data sources such as Foursquare and Yelp.

```
usage: predict_decors.py [-h] -latitude LATITUDE -longitude LONGITUDE
                         [-radius RADIUS] [-date DATE]
                         [-foursquare_api_key FOURSQUARE_API_KEY]
                         [-google_places_api_key GOOGLE_PLACES_API_KEY]
                         [-yelp_api_key YELP_API_KEY] [-debug]

arguments:
  -latitude LATITUDE    Latitude for where to look for decors. Must be a value
                        between -90.0 and 90.0
  -longitude LONGITUDE  Longitude for where to look for decors. Must be a
                        value between -180.0 and 180.
  -radius RADIUS        Radius for how far to predict the decors. Given in
                        meters, each dataset has its own rules as to how large
                        this radius can be.
  -date DATE            Date formatted as m/d/Y, IE 12/18/2021.
  -foursquare_api_key FOURSQUARE_API_KEY
  -google_places_api_key GOOGLE_PLACES_API_KEY
  -yelp_api_key YELP_API_KEY
  -debug                Add this flag to print extra debug info.
```
## analyze_dataset.py
Command Line Tool for loading a dataset based on the Pikmin Bloom Decor
Database, running its data through various data sources (IE, OpenStreetMap,
Foursquare, etc.) and analyzing the accuracy of tags. The point of this script
is to try to nail down whichtags from which data sources are used to make
decor Pikmin spawn.
```
usage: analyze_dataset.py [-h] [-input_file INPUT_FILE] [-pull_latest_data]
                          [-output_file OUTPUT_FILE] [-email EMAIL]
                          [-foursquare_api_key FOURSQUARE_API_KEY]
                          [-google_places_api_key GOOGLE_PLACES_API_KEY]
                          [-yelp_api_key YELP_API_KEY] [-invalidate_caches]
                          [-debug]

arguments:
  -input_file INPUT_FILE
                        Input file, a CSV that contains pikmin decors. Either
                        this, or pull_latest_data is required
  -pull_latest_data     Pulls latest data instead of using an input file.
                        Either this, or input_file is required.
  -output_file OUTPUT_FILE
                        Output file, a CSV that stores the predictions from
                        data sources like OSM.

  -email EMAIL          Email for Nominatim, required to convert location data
                        to GPS.
  -foursquare_api_key FOURSQUARE_API_KEY
  -google_places_api_key GOOGLE_PLACES_API_KEY
  -yelp_api_key YELP_API_KEY

  -invalidate_caches    Add this flag to invalidate caches and run predictions
                        from scratch.
  -debug                Add this flag to print extra debug info.
```
## A Few Words on Credentials
- By default, OpenStreetMap queries will always work and will always be used. To do reverse GPS lookups while analyzing datasets, an email is required for the Nominatim.
- To use Foursquare, Yelp, or Google Places, a developer account is needed for each.
  - [Foursquare Getting Started Guide](https://developer.foursquare.com/docs/places-api-getting-started)
  - [Yelp Developer Docs](https://www.yelp.com/developers/documentation/v3)
  - [Google Places Developer Docs](https://developers.google.com/maps/documentation/places/web-service/overview) (note this requires you input a credit card)
- The scripts will only use data sources other than OpenStreetMap if the API key is passed in as a command line argument to the script.

## FAQ

### Where are the Tags Mapped to Decors?
This is the [file you're looking for](decor_to_tag_mapping.py).

### I think a tag is wrong and leading to incorrect predictions, what should I do?
We don't know for certain what is used in-game, so it is very possible that tags are wrong. We're trying to update this model as we go. To help update the model, submit an issue to this repo, with at least 3 example locations that prove your case. Be as specific with the example as possible, IE, provide a picture of the decor tag in-game, the GPS coordinate for the sample, and any links to websites that prove your case.

### Where is the analyze_dataset script getting data?
The script is using the [Pikmin Bloom Decor Database](https://docs.google.com/spreadsheets/d/1gCrsXoeZ97eGwm9g4_yuB7RXChnKfLqYh1hUJ54Cnjs/edit#gid=857493320) as its main data source. If you want to submit your own results, use [this form](https://docs.google.com/forms/d/e/1FAIpQLSeEG0fo_L0DDcUqKcT_j8cpCNVzc6REZcvOLE09Ej1fPn8aZg/viewform).

### Are all these data sources (Foursquare, Yelp, etc.) actually used in the game? Which ones are most important?
We're extremely confident that OpenStreetMap and Foursquare are both used, so if you were to set up only one developer account, make it Foursquare. There are a fair number of samples that can only be explained by Yelp, and a small handful of samples that only map to Google Places, so our confidence is lower for these two data sources. We provide them as an option here to help rule them in/rule them out.

### How do I install this script?
This script assumes a basic knowledge of python setup and that the user is using Python 3.6+. If you're new to python, I'd recommend using virtual environments, managed by either [pyenv](https://github.com/pyenv/pyenv) (command-line solution) or [PyCharm CE](https://www.jetbrains.com/pycharm/download/) (Jetbrains GUI based solution). The reason for a tool to manage your environments is if you want to run more scripts with other dependencies in the future, you don't want the configuration for one script to break running another, so having each script run in its own virtual environment keeps everything nice and happy.

Once you've got a solution for managing Python environments set up, you'll want to use the [requirements.txt](requirements.txt) which specifies which dependencies the scripts use.
- For PyCharm CE, check [here](https://www.jetbrains.com/help/pycharm/managing-dependencies.html) for a guide.
- For a command line approach, run `python3 -m pip install -r requirements.txt`


### The script timed out/it was canceled part way through. How do I recover?
There are no plans to add retries to the script. Caches are built as the script finishes any given step. If it fails due to a data source timeout, a temporary loss of internet, etc., rerun the script, it'll skip whatever work was already cached.

### What is the analyze_dataset script doing?
- It loads data by either loading the file at `-input_file` or if the user passed `-pull_latest_data`, it pulls the data from Google Sheets and preprocesses it to be in the proper format.
- Once it has its initial data, it loops through each row and maps every `County`, `State`, `Country` to a location on OSM.
- Once it has location data, it goes through each data source that the user has access to, and runs a prediction based on the location information from the previous step and the name of the location.
- Once it has context from all data sources, the dataset is filtered so that locations that can't be found in any data source are skipped. Duplicates are also removed, and a few other smaller filtering rules are applied.
- Once that dataset is prepped, it runs through every entry once more, and creates an array of potential decors per business in the dataset.
- Finally, it checks the array of potential decors against which decor was given in the dataset, and scores the final result.

## Known Issues and Shortcomings
- **McDonald's Problem:** When analyzing a dataset, we base our queries on the `County`, `State`, and `Country` to define the location, and the `name` of the location to narrow it down further. But what if there are two `"McDonalds'"` in the same county, and one is tagged as a _cafe_ and _restaurant_, while the other is tagged as a _burger_place_? In these cases, we wouldn't know _which_ McDonald's is used for the submission to the decor database, so inaccurate tags may be applied.  
- **Filtered Results Problem:** If you run the prediction script on a very dense area (IE a mall, or a busy city square) it will predict much more potential businesses than are currently in-game. There appears to be some filtering based off of popularity (IE, foursquare locations with more check-ins get priority), and it also appears that the game prefers variety over reflecting the most popular businesses (IE, a less popular sweetshop takes priority over more popular restaurants, if there are plenty of restaurants nearby). The filtering rules are not yet known, so the script gives all possible options it detects.
- **Outline to Tag Mapping Problem:** When analyzing a dataset, certain tags, IE Waterside and Beach, will not give a specific body of water or body of sand as their location name, and instead will re-use their `County` name again. We believe this only happens to tags with outlines on OpenStreetMap. If a cell falls in an outlined tag, it may give the `County` instead of the name of the outline. This makes it difficult to analyze a subset of decors since these will often have too little data in the game to lookup a GPS coordinate for.

## License
Copyright 2022

Code licensed under the MIT License: <http://opensource.org/licenses/MIT>
