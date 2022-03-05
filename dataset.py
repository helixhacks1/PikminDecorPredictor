from enum import Enum


class Dataset(str, Enum):
    osm = "OSM"
    google_places = "GooglePlaces"
    yelp = "Yelp"
    foursquare = "Foursquare"
